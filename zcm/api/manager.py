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
from datetime import datetime
from pathlib import Path

from zcm.api.clone import Clone
from zcm.exceptions import ZCMError, ZCMException
from zcm.lib.zfs import (zfs_clone, zfs_create, zfs_destroy, zfs_exists,
                         zfs_inherit, zfs_list, zfs_promote, zfs_set,
                         zfs_snapshot)

log = logging.getLogger(__name__)

def get_zcm_for_path(path_str):
    zfs_list_output = zfs_list(zfs_type='filesystem', properties=[
                               'name', 'zfs_clone_manager:path', 'zfs_clone_manager:active'])
    for zfs in zfs_list_output:
        if str(zfs['zfs_clone_manager:path']) == path_str and zfs['zfs_clone_manager:active'] is None:
            return zfs['name']
    return None


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
        zfs_list_output = zfs_list(properties=['name',
                                               'zfs_clone_manager:path', 'zfs_clone_manager:active'], recursive=True)
        return [Manager(zfs['name']) for zfs in zfs_list_output if zfs['zfs_clone_manager:path']
                is not None and zfs['zfs_clone_manager:active'] is None]

    @staticmethod
    def initialize_zfs(zfs_str, path_str):
        path = Path(path_str)
        if path.exists():
            raise ZCMError('Path %s already exists, can not use it' % path_str)
        if zfs_exists(zfs_str):
            raise ZCMError('ZFS %s already created, can not use it' % zfs_str)
        zfs = zfs_create('00000000', zfs_str, mountpoint=path,
                         recursive=True, zcm_active=True)
        if zfs is None:
            raise ZCMError('Could not clone ZFS %s at %s' %
                           (zfs_str, path_str))
        zfs_set(zfs_str, mountpoint=Path(path, '.clones'), zcm_path=path_str)
        log.info('Created ZCM %s at path %s' % (zfs_str, path_str))

    def load(self):
        self.clones = []
        self.older_clones = []
        self.newer_clones = []
        self.active_clone = None
        self.next_id = None
        self.size = None
        if not isinstance(self.zfs, str):
            raise ZCMError('The name property is invalid: ' + str(self.zfs))
        last_id = 0
        zfs_list_output = zfs_list(self.zfs, zfs_type='filesystem', properties=[
                                    'name', 'zfs_clone_manager:path', 'zfs_clone_manager:active', 'origin', 'mountpoint', 'creation', 'used'], recursive=True)
        for zfs in zfs_list_output:
            if zfs['name'] == self.zfs:
                if zfs['zfs_clone_manager:active'] is not None:
                    log.warning('The zfs_clone_manager:active property must not be set in root zfs ' + self.zfs)
                    zfs_inherit(self.zfs, 'zfs_clone_manager:active')
                self.path = zfs['zfs_clone_manager:path']
            else:
                id = zfs['name'].split('/')[-1]
                last_id = max(last_id, int(id, base=16))
                origin_id = snapshot_to_origin_id(zfs['origin'])
                clone = Clone(id, zfs['name'], zfs['origin'], origin_id,
                                zfs['mountpoint'], zfs['creation'], zfs['used'])
                if not isinstance(self.path, Path) or not self.path.is_dir():
                    raise ZCMError('The path property is invalid: ' + self.path)
                if zfs['mountpoint'] == self.path:
                    self.active_clone = clone
                else:
                    if self.active_clone:
                        self.newer_clones.append(clone)
                    else:
                        self.older_clones.append(clone)
                self.clones.append(clone)
        self.next_id = format(last_id + 1, '08x')

    def create(self, max_newer=None, max_total=None, auto_remove=False):
        if not self.active_clone:
            raise ZCMError('There is no active clone, activate one first')
        if not auto_remove and max_newer is not None and len(self.newer_clones) >= max_newer:
            raise ZCMException(
                'There are already %d newer clones, can not create another' % len(self.newer_clones))
        if not auto_remove and max_total is not None and len(self.clones) >= max_total:
            raise ZCMException(
                'There are already %d clones, can not create another' % len(self.clones))
        id = self.next_id
        snapshot = zfs_snapshot(id, self.active_clone.zfs)
        if snapshot is None:
            raise ZCMError('Could not create ZFS snapshot %s@%s' %
                           (self.active_clone.zfs, id))
        zfs = zfs_clone(self.zfs + '/' + id, snapshot, zcm_active=False)
        if zfs is None:
            raise ZCMError('Could not create ZFS clone %s/%s' %
                           (self.zfs, id))
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
        failed = []
        for clone in self.clones:
            if clone != self.active_clone:
                if zfs_set(clone.zfs, mounted=False) != 0:
                    failed.append(clone.zfs)
        if zfs_set(self.zfs, mounted=False) != 0:
            failed.append(self.zfs)
        if self.active_clone is not None:
            if zfs_set(self.active_clone.zfs, mounted=False) != 0:
                failed.append(self.active_clone.zfs)
        if failed:
            # at lest one unmount failed, remount all and fail
            self.mount()
            raise ZCMError('Failed to unmount %s, device(s) in use' %
                           ' and'.join(failed))

    def mount(self):
        if not self.active_clone:
            raise ZCMError('There is no active clone, activate one first')
        zfs_set(self.active_clone.zfs, mounted=True)
        zfs_set(self.zfs, mounted=True)
        for clone in self.clones:
            if clone != self.active_clone:
                zfs_set(clone.zfs, mounted=True)

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
        if self.active_clone is not None:
            zfs_inherit(self.active_clone.zfs, 'mountpoint')
            zfs_set(self.active_clone.zfs, zcm_active=False)
        zfs_set(next_active.zfs, mountpoint=self.path, zcm_active=True)
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
        zfs_destroy(clone.zfs)
        if clone.origin:
            zfs_destroy(clone.origin)
        if promoted:
            zfs_destroy('%s@%s' % (promoted.zfs, promoted.id))
        log.info('Removed clone ' + clone.id)
        self.load()

    def destroy(self):
        self.unmount()
        if zfs_destroy(self.zfs, recursive=True) != 0:
            raise ZCMError('Could not destroy ZFS ' + self.zfs)
        try:
            self.path.rmdir()
        except OSError as e:
            raise ZCMError('Could not destroy path ' + self.path)
