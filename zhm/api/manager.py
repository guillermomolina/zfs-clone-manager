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

from zhm.api.print import format_bytes
from zhm.exceptions import ZHMError

from .print import print_table
from .zfs import (zfs_clone, zfs_create, zfs_destroy, zfs_exists, zfs_get,
                  zfs_inherit, zfs_is_filesystem, zfs_list, zfs_promote,
                  zfs_rename, zfs_set, zfs_snapshot)

log = logging.getLogger(__name__)


def get_zfs_for_path(path):
    hidden_path = Path(path, '.clones')
    zfs_list_output = zfs_list(
        str(hidden_path), zfs_type='filesystem', properties=['name', 'mountpoint'])
    if len(zfs_list_output) == 1 and zfs_list_output[0]['mountpoint'] == hidden_path:
        zfs = zfs_list_output[0]['name']
        return zfs
    raise ZHMError('The path %s is invalid or uninitialized' % path)


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
    def __init__(self, path):
        self.path = Path(path)
        self.zfs = None
        self.instances = []
        self.active = None
        self.next_id = None
        self.load()

    @staticmethod
    def initialize_zfs(zfs, path_str):
        path = Path(path_str)
        if path.exists():
            raise ZHMError('Path %s already exists, can not use it' % path_str)
        if zfs_exists(zfs):
            raise ZHMError('ZFS %s already created, can not use it' % zfs)
        instance = zfs_create('00000000', zfs, mountpoint=path, recursive=True)
        if instance is None:
            raise ZHMError('Could not clone ZFS %s at %s' % (zfs, path_str))
        zfs_set(zfs, mountpoint=Path(path, '.clones'))
        log.info('Created ZHM %s at path %s' % (zfs, path_str))

    def load(self):
        self.instances = []
        self.active = None
        self.next_id = None
        if self.path.is_dir():
            self.zfs = get_zfs_for_path(self.path)
            last_id = 0
            zfs_list_output = zfs_list(self.zfs, zfs_type='filesystem', properties=[
                                       'name', 'origin', 'mountpoint', 'creation', 'used'], recursive=True)
            for zfs in zfs_list_output:
                if zfs['name'] == self.zfs:
                    self.used = zfs['used']
                else:
                    zfs['id'] = zfs['name'].split('/')[-1]
                    last_id = max(last_id, int(zfs['id'], base=16))
                    zfs['origin_id'] = snapshot_to_origin_id(zfs['origin'])
                    if zfs['mountpoint'] == self.path:
                        self.active = zfs
                    self.instances.append(zfs)
            self.next_id = format(last_id + 1, '08x')

    def clone(self):
        if not self.active:
            raise ZHMError('There is no active instance, activate one first')
        snapshot = zfs_snapshot(self.next_id, self.active['name'])
        zfs = zfs_clone(self.zfs + '/' + self.next_id, snapshot)
        instance = {
            'id': self.next_id,
            'name': zfs,
            'origin': snapshot,
            'mountpoint': zfs_get(zfs, 'mountpoint')
        }
        self.instances.append(instance)
        log.info('Created instance ' + instance['id'])
        self.load()
        return instance

    def get_instance(self, id):
        for instance in self.instances:
            if instance['id'] == id:
                return instance
        raise ZHMError('There is no instance with id ' + id)

    def unmount(self):
        failed = []
        for instance in self.instances:
            if instance != self.active:
                if zfs_set(instance['name'], mounted=False) != 0:
                    failed.append(instance['name'])
        if zfs_set(self.zfs, mounted=False) != 0:
            failed.append(self.zfs)
        if self.active is not None:
            if zfs_set(self.active['name'], mounted=False) != 0:
                failed.append(self.active['name'])
        if failed:
            # at lest one unmount failed, remount all and fail
            self.mount()
            raise ZHMError('Failed to unmount %s, device(s) in use' %
                           ' and'.join(failed))

    def mount(self):
        if not self.active:
            raise ZHMError('There is no active instance, activate one first')
        zfs_set(self.active['name'], mounted=True)
        zfs_set(self.zfs, mounted=True)
        for instance in self.instances:
            if instance != self.active:
                zfs_set(instance['name'], mounted=True)

    def activate(self, id):
        instance = self.get_instance(id)
        if instance == self.active:
            log.warning('Instance %s already active', id)
            return instance

        self.unmount()
        if self.active is not None:
            zfs_inherit(self.active['name'], 'mountpoint')
        zfs_set(instance['name'], mountpoint=self.path)
        self.active = instance
        self.mount()

        log.info('Activated instance ' + id)
        self.load()
        return instance

    def find_clones(self, id):
        clones = []
        for instance in self.instances:
            if instance['origin_id'] == id:
                clones.append(instance)
        return clones

    def remove(self, id):
        instance = self.get_instance(id)
        if instance == self.active:
            raise ZHMError(
                'Instance with id %s is active, can not remove' % id)
        clones = self.find_clones(id)
        promoted = None
        if clones:
            promoted = clones[-1]
            zfs_promote(promoted['name'])
        zfs_destroy(instance['name'])
        if instance['origin']:
            zfs_destroy(instance['origin'])
        if promoted:
            zfs_destroy('%s@%s' % (promoted['name'], promoted['id']))
        self.load()

    def print(self, truncate=True):
        table = []
        for instance in self.instances:
            table.append({
                'a': '*' if self.active == instance else ' ',
                'id': instance['id'],
                'mountpoint': instance['mountpoint'],
                'origin': instance['origin_id'] if instance['origin_id'] else '',
                'date': datetime.fromtimestamp(instance['creation']),
                'size': format_bytes(instance['used'])
            })
        print_table(table, truncate=truncate)

    def destroy(self):
        self.unmount()
        if zfs_destroy(self.zfs, recursive=True) != 0:
            raise ZHMError('Could not destroy ZFS ' + self.zfs)
        try:
            self.path.rmdir()
        except OSError as e:
            raise ZHMError('Could not destroy path ' + self.path)
