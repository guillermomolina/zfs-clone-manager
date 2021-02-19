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

import unittest
from pathlib import Path

from zcm.api.manager import Manager
from zcm.exceptions import ZCMError, ZCMException
from zcm.lib.zfs import zfs_exists, zfs_get, zfs_is_filesystem

zfs = 'rpool/my/cool/zfs/directory'
directory = '/my_cool_zfs_directory'


class TestAPI(unittest.TestCase):
    def setUp(self):
        try:
            Manager.initialize_zfs(zfs, directory)
        except ZCMError:
            pass
        return super().setUp()

    def tearDown(self):
        try:
            Manager(directory).destroy()
        except ZCMError:
            pass
        return super().tearDown()

    def test_initialize(self):
        with self.assertRaises(ZCMError):
            Manager.initialize_zfs(zfs, directory)
        clone = None
        try:
            manager = Manager(directory)
        except ZCMError as e:
            self.fail('Instantiation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active_clone, manager.clones[0])
        self.assertEqual(manager.next_id, '00000001')
        self.assertEqual(len(manager.older_clones), 0)
        self.assertEqual(len(manager.newer_clones), 0)

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.clones[0].id, id)
        self.assertEqual(manager.clones[0].zfs, filesystem)
        self.assertIsNone(manager.clones[0].origin)
        self.assertIsNone(manager.clones[0].origin_id)
        self.assertEqual(manager.clones[0].mountpoint, path)
        self.assertIsInstance(manager.clones[0].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_create_1(self):
        clone = None
        try:
            manager = Manager(directory)
        except ZCMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active_clone, manager.clones[0])
        self.assertEqual(manager.next_id, '00000002')
        self.assertEqual(len(manager.older_clones), 0)
        self.assertEqual(len(manager.newer_clones), 1)

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.clones[0].id, id)
        self.assertEqual(manager.clones[0].zfs, filesystem)
        self.assertIsNone(manager.clones[0].origin)
        self.assertIsNone(manager.clones[0].origin_id)
        self.assertEqual(manager.clones[0].mountpoint, path)
        self.assertIsInstance(manager.clones[0].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.clones[1].id, id)
        self.assertEqual(manager.clones[1].zfs, filesystem)
        self.assertEqual(manager.clones[1].origin, '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.clones[1].origin_id, '00000000')
        self.assertEqual(manager.clones[1].mountpoint, path)
        self.assertIsInstance(manager.clones[1].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_activate_1(self):
        clone = None
        try:
            manager = Manager(directory)
        except ZCMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.activate('00000001')
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        with self.assertRaises(ZCMException):
            manager.activate('00000001')
        with self.assertRaises(ZCMError):
            manager.remove('00000001')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active_clone, manager.clones[1])
        self.assertEqual(manager.next_id, '00000002')
        self.assertEqual(len(manager.older_clones), 1)
        self.assertEqual(len(manager.newer_clones), 0)

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.clones[0].id, id)
        self.assertEqual(manager.clones[0].zfs, filesystem)
        self.assertIsNone(manager.clones[0].origin)
        self.assertIsNone(manager.clones[0].origin_id)
        self.assertEqual(manager.clones[0].mountpoint, path)
        self.assertIsInstance(manager.clones[0].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.clones[1].id, id)
        self.assertEqual(manager.clones[1].zfs, filesystem)
        self.assertEqual(manager.clones[1].origin, '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.clones[1].origin_id, '00000000')
        self.assertEqual(manager.clones[1].mountpoint, path)
        self.assertIsInstance(manager.clones[1].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_remove_newer_1(self):
        clone = None
        try:
            manager = Manager(directory)
        except ZCMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.remove('00000001')
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active_clone, manager.clones[0])
        self.assertEqual(manager.next_id, '00000001')
        self.assertEqual(len(manager.older_clones), 0)
        self.assertEqual(len(manager.newer_clones), 0)

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.clones[0].id, id)
        self.assertEqual(manager.clones[0].zfs, filesystem)
        self.assertIsNone(manager.clones[0].origin)
        self.assertIsNone(manager.clones[0].origin_id)
        self.assertEqual(manager.clones[0].mountpoint, path)
        self.assertIsInstance(manager.clones[0].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertFalse(zfs_exists(filesystem))
        self.assertFalse(path.exists())

    def test_remove_older_1(self):
        clone = None
        try:
            manager = Manager(directory)
        except ZCMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.activate('00000001')
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.remove('00000000')
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active_clone, manager.clones[0])
        self.assertEqual(manager.next_id, '00000002')
        self.assertEqual(len(manager.older_clones), 0)
        self.assertEqual(len(manager.newer_clones), 0)

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertFalse(zfs_exists(filesystem))
        self.assertFalse(path.exists())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.clones[0].id, id)
        self.assertEqual(manager.clones[0].zfs, filesystem)
        self.assertIsNone(manager.clones[0].origin)
        self.assertIsNone(manager.clones[0].origin_id)
        self.assertEqual(manager.clones[0].mountpoint, path)
        self.assertIsInstance(manager.clones[0].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_create_2(self):
        clone = None
        try:
            manager = Manager(directory)
        except ZCMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active_clone, manager.clones[0])
        self.assertEqual(manager.next_id, '00000003')
        self.assertEqual(len(manager.older_clones), 0)
        self.assertEqual(len(manager.newer_clones), 2)

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.clones[0].id, id)
        self.assertEqual(manager.clones[0].zfs, filesystem)
        self.assertIsNone(manager.clones[0].origin)
        self.assertIsNone(manager.clones[0].origin_id)
        self.assertEqual(manager.clones[0].mountpoint, path)
        self.assertIsInstance(manager.clones[0].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.clones[1].id, id)
        self.assertEqual(manager.clones[1].zfs, filesystem)
        self.assertEqual(manager.clones[1].origin, '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.clones[1].origin_id, '00000000')
        self.assertEqual(manager.clones[1].mountpoint, path)
        self.assertIsInstance(manager.clones[1].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000002'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.clones[2].id, id)
        self.assertEqual(manager.clones[2].zfs, filesystem)
        self.assertEqual(manager.clones[2].origin, '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.clones[2].origin_id, '00000000')
        self.assertEqual(manager.clones[2].mountpoint, path)
        self.assertIsInstance(manager.clones[1].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_activate_2(self):
        clone = None
        try:
            manager = Manager(directory)
        except ZCMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.activate('00000001')
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        with self.assertRaises(ZCMException):
            manager.activate('00000001')
        with self.assertRaises(ZCMError):
            manager.remove('00000001')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active_clone, manager.clones[1])
        self.assertEqual(manager.next_id, '00000003')
        self.assertEqual(len(manager.older_clones), 1)
        self.assertEqual(len(manager.newer_clones), 1)

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.clones[0].id, id)
        self.assertEqual(manager.clones[0].zfs, filesystem)
        self.assertIsNone(manager.clones[0].origin)
        self.assertIsNone(manager.clones[0].origin_id)
        self.assertEqual(manager.clones[0].mountpoint, path)
        self.assertIsInstance(manager.clones[0].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.clones[1].id, id)
        self.assertEqual(manager.clones[1].zfs, filesystem)
        self.assertEqual(manager.clones[1].origin, '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.clones[1].origin_id, '00000000')
        self.assertEqual(manager.clones[1].mountpoint, path)
        self.assertIsInstance(manager.clones[1].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000002'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.clones[2].id, id)
        self.assertEqual(manager.clones[2].zfs, filesystem)
        self.assertEqual(manager.clones[2].origin, '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.clones[2].origin_id, '00000000')
        self.assertEqual(manager.clones[2].mountpoint, path)
        self.assertIsInstance(manager.clones[2].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_remove_newer_2(self):
        clone = None
        try:
            manager = Manager(directory)
        except ZCMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.activate('00000001')
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.remove('00000002')
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active_clone, manager.clones[1])
        self.assertEqual(manager.next_id, '00000002')
        self.assertEqual(len(manager.older_clones), 1)
        self.assertEqual(len(manager.newer_clones), 0)

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.clones[0].id, id)
        self.assertEqual(manager.clones[0].zfs, filesystem)
        self.assertIsNone(manager.clones[0].origin)
        self.assertIsNone(manager.clones[0].origin_id)
        self.assertEqual(manager.clones[0].mountpoint, path)
        self.assertIsInstance(manager.clones[0].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.clones[1].id, id)
        self.assertEqual(manager.clones[1].zfs, filesystem)
        self.assertEqual(manager.clones[1].origin, '%s/%s@%s' % (zfs, '00000000', id))
        self.assertEqual(manager.clones[1].origin_id, '00000000')
        self.assertEqual(manager.clones[1].mountpoint, path)
        self.assertIsInstance(manager.clones[1].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000002'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertFalse(zfs_exists(filesystem))
        self.assertFalse(path.exists())

    def test_remove_older_2(self):
        clone = None
        try:
            manager = Manager(directory)
        except ZCMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.activate('00000001')
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        try:
            manager.remove('00000000')
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active_clone, manager.clones[0])
        self.assertEqual(manager.next_id, '00000003')
        self.assertEqual(len(manager.older_clones), 0)
        self.assertEqual(len(manager.newer_clones), 1)

        filesystem = zfs
        path = Path(directory, '.clones')
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000000'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertFalse(zfs_exists(filesystem))
        self.assertFalse(path.exists())

        id = '00000001'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory)
        self.assertEqual(manager.clones[0].id, id)
        self.assertEqual(manager.clones[0].zfs, filesystem)
        self.assertEqual(manager.clones[0].origin, '%s/%s@%s' % (zfs, '00000002', id))
        self.assertEqual(manager.clones[0].origin_id, '00000002')
        self.assertEqual(manager.clones[0].mountpoint, path)
        self.assertIsInstance(manager.clones[0].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

        id = '00000002'
        filesystem = '%s/%s' % (zfs, id)
        path = Path(directory, '.clones', id)
        self.assertEqual(manager.clones[1].id, id)
        self.assertEqual(manager.clones[1].zfs, filesystem)
        self.assertIsNone(manager.clones[1].origin)
        self.assertIsNone(manager.clones[1].origin_id)
        self.assertEqual(manager.clones[1].mountpoint, path)
        self.assertIsInstance(manager.clones[1].creation, int)
        self.assertTrue(zfs_is_filesystem(filesystem))
        self.assertEqual(zfs_get(filesystem, 'mountpoint'), path)
        self.assertTrue(zfs_get(filesystem, 'mounted'))
        self.assertTrue(path.is_dir())

    def test_clone_options(self):
        clone = None
        try:
            manager = Manager(directory)
        except ZCMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.create()
            manager.create()
            manager.create()
            manager.create()
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        with self.assertRaises(ZCMException):
            manager.create(max_newer=5)
        with self.assertRaises(ZCMException):
            manager.create(max_total=6)

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active_clone, manager.clones[0])
        self.assertEqual(manager.next_id, '00000006')
        self.assertEqual(len(manager.older_clones), 0)
        self.assertEqual(len(manager.newer_clones), 5)

    def test_activate_options(self):
        clone = None
        try:
            manager = Manager(directory)
        except ZCMError as e:
            self.fail('Instantiation should not raise exceptions')
        try:
            manager.create()
            manager.create()
            manager.create()
            manager.create()
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')
        with self.assertRaises(ZCMException):
            manager.activate('00000002', max_newer=1)
        with self.assertRaises(ZCMException):
            manager.activate('00000002', max_older=1)
        try:
            manager.activate('00000002', max_older=2, max_newer=2)
        except ZCMError as e:
            self.fail('Creation should not raise exceptions')

        self.assertEqual(manager.path, Path(directory))
        self.assertEqual(manager.zfs, zfs)
        self.assertEqual(manager.active_clone, manager.clones[2])
        self.assertEqual(manager.next_id, '00000005')
        self.assertEqual(len(manager.older_clones), 2)
        self.assertEqual(len(manager.newer_clones), 2)


if __name__ == '__main__':
    unittest.main()
