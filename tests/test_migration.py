# Copyright 2021, Guillermo Adrián Molina
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from datetime import datetime
from pathlib import Path

from zcm.api.manager import Manager
from zcm.exceptions import ZCMError, ZCMException
from zcm.lib.zfs import ZFSError, zfs_create, zfs_destroy

zfs = 'rpool/my/cool/zfs/directory'
directory = '/my_cool_zfs_directory'


class TestAPI(unittest.TestCase):
    def test_initialize_existing_zfs(self):
        path = Path(directory)
        self.assertIsNotNone(zfs_create(zfs, mountpoint=directory, recursive=True))
        temp_dir = path.joinpath('my', 'cool', 'subdirectory')
        temp_dir.mkdir(parents=True)
        temp_file = temp_dir.joinpath('file.txt')
        with temp_file.open('w', encoding ='utf-8') as f:
            f.write('SOME TEXT')
        with self.assertRaises(ZCMError):
            Manager.initialize_manager(zfs, directory)
        try:
            zfs_destroy(zfs)
        except ZFSError:
            self.fail('zfs_destroy should not raise exceptions')
        self.assertFalse(temp_file.exists())
        path.rmdir()

    def test_migrate_existing_zfs(self):
        path = Path(directory)
        self.assertIsNotNone(zfs_create(zfs, mountpoint=directory, recursive=True))
        temp_dir = path.joinpath('my', 'cool', 'subdirectory')
        temp_dir.mkdir(parents=True)
        temp_file = temp_dir.joinpath('file.txt')
        with temp_file.open('w', encoding ='utf-8') as f:
            f.write('SOME TEXT')
        with self.assertRaises(ZCMError):
            Manager.initialize_manager(zfs, directory)
        with self.assertRaises(ZCMError):
            Manager.initialize_manager(zfs, directory, migrate='PATH')
        try:
            Manager.initialize_manager(zfs, directory, migrate='ZFS')
        except ZCMException as e:
            self.fail('Initialization should not raise exceptions')
        manager = None
        try:
            manager = Manager(zfs)
        except ZCMException as e:
            self.fail('Instantiation should not raise exceptions')
        self.assertTrue(temp_file.is_file())
        with temp_file.open('r', encoding ='utf-8') as f:
            self.assertEqual(f.read(), 'SOME TEXT')
        try:
            manager.destroy()
        except ZCMException as e:
            self.fail('Destroy should not raise exceptions')

    def test_migrate_existing_path(self):
        path = Path(directory)
        temp_dir = path.joinpath('my', 'cool', 'subdirectory')
        temp_dir.mkdir(parents=True)
        temp_file = temp_dir.joinpath('file.txt')
        with temp_file.open('w', encoding ='utf-8') as f:
            f.write('SOME TEXT')
        with self.assertRaises(ZCMError):
            Manager.initialize_manager(zfs, directory)
        with self.assertRaises(ZCMError):
            Manager.initialize_manager(zfs, directory)
        with self.assertRaises(ZCMError):
            Manager.initialize_manager(zfs, directory, migrate='ZFS')
        try:
            Manager.initialize_manager(zfs, directory, migrate='PATH')
        except ZCMException as e:
            self.fail('Initialization should not raise exceptions')
        manager = None
        try:
            manager = Manager(zfs)
        except ZCMException as e:
            self.fail('Instantiation should not raise exceptions')
        self.assertTrue(temp_file.is_file())
        with temp_file.open('r', encoding ='utf-8') as f:
            self.assertEqual(f.read(), 'SOME TEXT')
        try:
            manager.destroy()
        except ZCMException as e:
            self.fail('Destroy should not raise exceptions')

if __name__ == '__main__':
    unittest.main()
