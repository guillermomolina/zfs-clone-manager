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

from pathlib import Path
import logging
from zhm.exceptions import ZHMError
from .zfs import zfs_list, zfs_snapshot, zfs_clone, zfs_get, zfs_inherit, zfs_set, zfs_promote, zfs_destroy, zfs_rename
from .print import print_table
from datetime import datetime

log = logging.getLogger(__name__)

def get_zfs_for_path(path):
    hidden_path = Path(path, '.clones')
    zfs_list_output = zfs_list(str(hidden_path), zfs_type='filesystem', properties=['name', 'mountpoint'])
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
        self.instances = []
        self.active = None
        self.zfs = None
        self.next_id = None
        self.load()

    def load(self):
        self.active = None
        if self.path.is_dir():
            self.zfs = get_zfs_for_path(self.path)
            last_id = 0
            zfs_list_output = zfs_list(self.zfs, zfs_type='filesystem', properties=['name','origin','mountpoint', 'creation'], recursive=True)
            for zfs in zfs_list_output:
                if zfs['name'] != self.zfs:
                    zfs['id'] = zfs['name'].split('/')[-1]
                    last_id = max(last_id, int(zfs['id'], base=16))
                    zfs['active'] = zfs['mountpoint'] == self.path
                    zfs['origin_id'] = snapshot_to_origin_id(zfs['origin'])
                    if zfs['active']:
                        self.active = zfs
                    self.instances.append(zfs)
            self.next_id = format(last_id + 1, '08x')


    def create(self):
        if not self.active:
            raise ZHMError('There is no active instance, activate one first')
        snapshot = zfs_snapshot(self.next_id, self.active['name'])
        zfs = zfs_clone(self.zfs + '/' + self.next_id, snapshot)
        instance = {
            'id': self.next_id,
            'name': zfs,
            'origin': snapshot,
            'mountpoint': zfs_get(zfs, 'mountpoint'),
            'active': False
        }
        self.instances.append(instance)
        log.info('Created instance ' + instance['id'])
        return instance

    def get_instance(self, id):
        for instance in self.instances:
            if instance['id'] == id:
                return instance
        raise ZHMError('There is no instance with id ' + id)

    def unmount(self):
        for instance in self.instances:
            if instance != self.active:
                zfs_set(instance['name'], mounted=False)
        zfs_set(self.zfs, mounted=False)        
        if self.active is not None:
            zfs_set(self.active['name'], mounted=False)

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
            raise ZHMError('Instance with id %s is active, can not remove' % id)
        clones = self.find_clones(id)
        promoted = None
        if clones:
            promoted = clones[-1]
            zfs_promote(promoted['name'])
        zfs_destroy(instance['name'])
        if instance['origin']:
            zfs_destroy(instance['origin'])
        if promoted:
            zfs_destroy('%s@%s' % (promoted['name'],promoted['id']))
        #self.load()

    def print(self, truncate=True):
        table = []
        for instance in self.instances:
            table.append({
                'a': '*' if instance['active'] else ' ',
                'id': instance['id'],
                'mountpoint': instance['mountpoint'],
                'origin': instance['origin_id'] if instance['origin_id'] else '',
                'date': datetime.utcfromtimestamp(instance['creation'])
            })
        print_table(table, truncate=truncate)