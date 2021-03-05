# Copyright 2021, Guillermo Adrián Molina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import shutil
from pathlib import Path

from zcm.api.clone import Clone
from zcm.exceptions import ZCMError, ZCMException
from zcm.lib.helpers import copy_directory, id_generator
from zcm.lib.zfs import (ZFSError, zfs_clone, zfs_create, zfs_destroy,
                         zfs_inherit, zfs_list, zfs_mount, zfs_promote,
                         zfs_rename, zfs_set, zfs_snapshot, zfs_unmount)

log = logging.getLogger(__name__)


def get_zcm_for_path(path_str):
    path = Path(path_str).absolute()
    if not path.is_dir():
        return None
    absolute_path_str = str(path)
    zfs_list_output = zfs_list(absolute_path_str, zfs_type='filesystem', properties=[
                               'name', 'zfs_clone_manager:path', 'mountpoint'])
    if len(zfs_list_output) != 1:
        return None
    zfs = zfs_list_output[0]
    if str(zfs['zfs_clone_manager:path']) == absolute_path_str and str(zfs['mountpoint']) == absolute_path_str:
        splitted_name = zfs['name'].split('/')
        name = '/'.join(splitted_name[:-1])
        try:
            int(splitted_name[-1], base=16)
        except ValueError:
            return None
        return name


def snapshot_to_origin_id(snapshot):
    # snapshot -> rpool/zfsa/zfsb/00000004@00000005
    # snapshot.split('/') -> ['rpool','zfsa','zfsb','00000004@00000005']
    # snapshot.split('/')[-1] -> '00000004@00000005'
    # snapshot.split('/')[-1].split('@') -> ['00000004','00000005']
    # snapshot.split('/')[-1].split('@')[0] -> '00000004'
    if snapshot:
        return snapshot.split('/')[-1].split('@')[0]
    return None


class Manager:
    def __init__(self, zfs_or_path):
        self.zfs = None
        self.path = None
        self.clones = []
        self.older_clones = []
        self.newer_clones = []
        self.active_clone = None
        self.next_id = None
        self.size = None
        zfs = get_zcm_for_path(zfs_or_path)
        self.zfs = zfs_or_path if zfs is None else zfs
        self.load()

    @staticmethod
    def get_managers():
        zfs_list_output = zfs_list(
            properties=['name', 'zfs_clone_manager:path', 'mountpoint'])
        return [Manager(zfs['name'])
                for zfs in zfs_list_output
                if zfs['zfs_clone_manager:path'] is not None and
                zfs['mountpoint'] == Path(zfs['zfs_clone_manager:path'], '.clones')]

    @staticmethod
    def initialize_manager(zfs_str, path_str, migrate=None):
        path = Path(path_str)
        zfs_list_output = zfs_list(zfs_str, zfs_type='all', properties=[
            'name', 'type', 'zfs_clone_manager:path', 'origin', 'mountpoint'], recursive=True)
        if zfs_list_output:
            zfs = zfs_list_output[0]
            if zfs['zfs_clone_manager:path']:
                raise ZCMError(
                    'The ZFS %s is a ZCM manager, will not initialize' % zfs_str)
            if len(zfs_list_output) > 1:
                raise ZCMError(
                    'The ZFS %s has children, can not initialize ZCM with it' % zfs_str)
            if zfs['type'] != 'filesystem':
                raise ZCMError('The ZFS %s is of type %s, can not initialize ZCM with it' % (
                    zfs_str, zfs['type']))
            if migrate != 'ZFS':
                raise ZCMError(
                    'ZFS %s already exists, will not initialize a manager with it' % zfs_str)
            if zfs['mountpoint'] != path and path.exists():
                 raise ZCMError(
                    'Path %s already exists (and it is not the ZFS %s mountpoint, can not use it' % (path_str, zfs_str))
            random_id = id_generator()
            zfs_parts = zfs_str.split('/')[:-1]
            zfs_parts.append(random_id)
            random_zfs = '/'.join(zfs_parts)
            try:
                zfs_unmount(zfs_str)
                zfs_rename(zfs_str, random_zfs)
                zfs_create(zfs_str, zcm_path=path_str, recursive=True)
                zfs_unmount(zfs_str)
                zfs_rename(random_zfs, zfs_str + '/00000000')
                zfs_set(zfs_str + '/00000000', mountpoint=path)
                zfs_mount(zfs_str + '/00000000')
                zfs_set(zfs_str, mountpoint=Path(path, '.clones'))
                zfs_mount(zfs_str)
                log.info('Migrated ZFS %s at path %s to ZCM' % (zfs_str, path_str))
            except ZFSError as e:
                raise ZCMError(e.message)            
            return
        original_path = None 
        if path.exists():
            if migrate != 'PATH':
                raise ZCMError(
                    'Path %s already exists, will not initialize a manager' % path_str)
            random_id = id_generator()
            original_path = Path(path.parents[0], random_id)
            path.rename(original_path) 
        try:
            zfs_create(zfs_str, zcm_path=path_str, recursive=True)
            zfs_unmount(zfs_str)
            zfs_create('00000000', zfs_str, mountpoint=path)
            zfs_set(zfs_str, mountpoint=Path(path, '.clones'))
            zfs_mount(zfs_str)
            log.info('Created ZCM %s at path %s' % (zfs_str, path_str))
        except ZFSError as e:
            raise ZCMError(e.message)
        if original_path:
            if copy_directory(original_path, path) != 0:
                raise ZCMError('Could not move content of original directory, kept at %s' % original_path)
            shutil.rmtree(original_path)
            log.info('Moved content of path %s to clone' % path_str)
           

    def load(self):
        if not isinstance(self.zfs, str):
            raise ZCMError(
                'The name property is invalid: ' + str(self.zfs))
        self.path = None
        self.clones = []
        self.older_clones = []
        self.newer_clones = []
        self.active_clone = None
        self.next_id = None
        self.size = None
        last_id = 0
        zfs_list_output = zfs_list(self.zfs, zfs_type='filesystem', properties=[
            'name', 'zfs_clone_manager:path', 'origin', 'mountpoint',
            'creation', 'used'], recursive=True)
        if not zfs_list_output:
            raise ZCMError(
                'There is no ZCM manager at %s' % self.zfs)
        for zfs in zfs_list_output:
            if self.path is None:
                self.zfs = zfs['name']
                if zfs['zfs_clone_manager:path'] is None:
                    raise ZCMError(
                        'The ZFS %s is not a valid ZCM manager' % zfs['name'])
                self.path = zfs['zfs_clone_manager:path']
                self.size = zfs['used']
            else:
                splitted_name = zfs['name'].split('/')
                name = '/'.join(splitted_name[:-1])
                id = splitted_name[-1]
                if name != self.zfs:
                    raise ZCMError(
                        'The ZFS %s is not a valid ZCM clone' % zfs['name'])
                try:
                    last_id = max(last_id, int(id, base=16))
                except ValueError:
                    raise ZCMError(
                        'The ZFS %s is not a valid ZCM clone' % zfs['name'])
                origin_id = snapshot_to_origin_id(zfs['origin'])
                clone = Clone(id, zfs['name'], zfs['origin'], origin_id,
                              zfs['mountpoint'], zfs['creation'], zfs['used'])
                if not isinstance(self.path, Path) or not self.path.is_dir():
                    raise ZCMError(
                        'The path property is invalid: ' + self.path)
                if zfs['mountpoint'] == self.path:
                    self.active_clone = clone
                else:
                    if self.active_clone:
                        self.newer_clones.append(clone)
                    else:
                        self.older_clones.append(clone)
                self.clones.append(clone)
        self.next_id = format(last_id + 1, '08x')

    def clone(self, max_newer=None, max_total=None, auto_remove=False):
        if not self.active_clone:
            raise ZCMError('There is no active clone, activate one first')
        if not auto_remove and max_newer is not None and len(self.newer_clones) >= max_newer:
            raise ZCMException(
                'There are already %d newer clones, can not create another' % len(self.newer_clones))
        if not auto_remove and max_total is not None and len(self.clones) >= max_total:
            raise ZCMException(
                'There are already %d clones, can not create another' % len(self.clones))
        id = self.next_id
        try:         
            snapshot = zfs_snapshot(id, self.active_clone.zfs)
            zfs = zfs_clone(self.zfs + '/' + id, snapshot)
        except ZFSError as e:
            raise ZCMError(e.message)            
        self.load()
        clone = self.get_clone(id)
        log.info('Created clone ' + clone.id)
        self.auto_remove(max_newer=max_newer, max_total=max_total)
        return clone

    def auto_remove(self, max_newer=None, max_older=None, max_total=None):
        while max_older is not None and len(self.older_clones) > max_older:
            self.remove(self.older_clones[0].id)
        while max_newer is not None and len(self.newer_clones) > max_newer:
            self.remove(self.newer_clones[0].id)
        while max_total is not None and len(self.clones) > max_total:
            if self.older_clones:
                self.remove(self.older_clones[0].id)
            elif self.newer_clones:
                self.remove(self.newer_clones[0].id)
            else:
                raise ZCMError(
                    'There are no more clones to remove in order to satisfy max limit of ' + max_total)

    def get_clone(self, id):
        for clone in self.clones:
            if clone.id == id:
                return clone
        raise ZCMError('There is no clone with id ' + id)

    def unmount(self):
        try:
            for clone in self.clones:
                if clone != self.active_clone:
                    zfs_unmount(clone.zfs)
            zfs_unmount(self.zfs)
            if self.active_clone is not None:
                zfs_unmount(self.active_clone.zfs)
        except ZFSError as e:
            # at lest one unmount failed, remount all and fail
            self.mount()
            raise ZCMError(e.message)

    def mount(self):
        if not self.active_clone:
            raise ZCMError('There is no active clone, activate one first')
        try:
            zfs_mount(self.active_clone.zfs)
            zfs_mount(self.zfs)
            for clone in self.clones:
                if clone != self.active_clone:
                    zfs_mount(clone.zfs)
        except ZFSError as e:
            raise ZCMError(e.message)

    def activate(self, id, max_newer=None, max_older=None, max_total=None, auto_remove=False):
        next_active = self.get_clone(id)
        if next_active == self.active_clone:
            raise ZCMException('Manager %s already active' % id)
        if not auto_remove and (max_newer is not None or max_older is not None):
            newer_count = 0
            older_count = 0
            has_reach_active = False
            for clone in self.clones:
                if clone == next_active:
                    has_reach_active = True
                else:
                    if has_reach_active:
                        newer_count += 1
                    else:
                        older_count += 1
            if not auto_remove and max_newer is not None and newer_count > max_newer:
                raise ZCMException(
                    'Command denied, Activating %s violates the maximum number of newer clones (%d/%d)'
                    % (id, newer_count, max_newer))
            if not auto_remove and max_older is not None and older_count > max_older:
                raise ZCMException(
                    'Command denied, Activating %s violates the maximum number of older clones (%d/%d)'
                    % (id, older_count, max_older))

        self.unmount()
        try:
            if self.active_clone is not None:
                zfs_inherit(self.active_clone.zfs, 'mountpoint')
            zfs_set(next_active.zfs, mountpoint=self.path)
        except ZFSError as e:
            raise ZCMError(e.message)
        self.active_clone = next_active
        self.mount()

        log.info('Activated clone ' + id)
        self.load()
        self.auto_remove(max_newer=max_newer,
                         max_older=max_older, max_total=max_total)
        return next_active

    def find_clones_with_origin(self, id):
        clones = []
        for clone in self.clones:
            if clone.origin_id == id:
                clones.append(clone)
        return clones

    def remove(self, id):
        clone = self.get_clone(id)
        if clone == self.active_clone:
            raise ZCMError(
                'Manager with id %s is active, can not remove' % id)
        clones = self.find_clones_with_origin(id)
        promoted = None
        if clones:
            promoted = clones[-1]
            zfs_promote(promoted.zfs)
        try:
            zfs_destroy(clone.zfs)
            if clone.origin:
                zfs_destroy(clone.origin)
            if promoted:
                zfs_destroy('%s@%s' % (promoted.zfs, promoted.id))
            log.info('Removed clone ' + clone.id)
            self.load()
        except ZFSError as e:
            raise ZCMError(e.message)            
        

    def destroy(self):
        try:
            self.unmount()
            zfs_destroy(self.zfs, recursive=True)
            self.path.rmdir()
        except ZFSError as e:
            raise ZCMError(e.message)            
        except OSError as e:
            raise ZCMError('Could not destroy path ' + self.path)

    def to_dictionary(self):
        return {
            'zfs': self.zfs,
            'path': str(self.path),
            'size': self.size,
            'clones': [ clone.id for clone in self.clones ],
            'older_clones': [ clone.id for clone in self.older_clones ],
            'newer_clones': [ clone.id for clone in self.newer_clones ],
            'active_clone': self.active_clone.id,
            'next_id': self.next_id
        }
