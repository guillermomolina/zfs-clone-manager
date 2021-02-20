# Copyright 2020, Guillermo Adrián Molina
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


import io
import logging
import pathlib
import subprocess

log = logging.getLogger(__name__)


def get_cmd(command,  arguments, options):
    cmd = ['/usr/sbin/zfs', command]
    if options is not None:
        for option in options:
            cmd += ['-o', '"' + option + '"']
    if arguments is not None:
        cmd += arguments
    log.debug('Running command: "' + ' '.join(cmd) + '"')
    return cmd


def _zfs(command,  arguments=None, options=None, stdout=None):
    cmd = get_cmd(command, arguments, options)
    return subprocess.Popen(cmd, stdout=stdout)


def zfs(command,  arguments=None, options=None):
    cmd = get_cmd(command, arguments, options)
    process = subprocess.run(cmd, capture_output=True, text=True)
    #import debugpy
    # debugpy.breakpoint()
    if process.stdout:
        for line in iter(process.stdout.splitlines()):
            log.info(line)
    if process.stderr:
        for line in iter(process.stderr.splitlines()):
            if process.returncode == 0:
                log.warning(line)
            else:
                log.error(line)
    return process.returncode


def zfs_create(zfs_name, parent=None, mountpoint=None, compression=None, recursive=False, zcm_path=None, zcm_active=None):
    filesystem = zfs_name
    if parent is None:
        last_index = zfs_name.rfind('/')
        parent = filesystem[:last_index]
        zfs_name = filesystem[last_index+1:]
    else:
        filesystem = '%s/%s' % (parent, zfs_name)

    if recursive:
        zfs_path = ''
        is_zpool = True
        for zfs_fs in parent.split('/'):
            zfs_path += '/' if zfs_path else ''
            zfs_path += zfs_fs
            if not zfs_is_filesystem(zfs_path):
                if is_zpool:
                    return None
                if zfs('create', [zfs_path]) != 0:
                    return None
                # For watever reason can not set mountpoint at creation time
                # We set this afterwards
                #zfs_set(zfs_path, mountpoint=None)
                
            is_zpool = False

    # Just debugging, don't fail if already created
    # if(destroy(filesystem, recursive=True) == 0):
    #    print('WARNING: Deleting filesystem (%s) ' % filesystem)

    options = []
    if compression is not None:
        options.append('compression=' + compression)
    if zcm_path is not None:
        options.append('zfs_clone_manager:path=' + str(zcm_path))
    if len(options) == 0:
        options = None
    if zfs('create', [filesystem], options) == 0:
        # For watever reason can not set this properties at creation time
        # We set them afterwards
        if mountpoint is not None:
            zfs_set(filesystem, mountpoint=mountpoint)
        if zcm_active is not None:
            zfs_set(filesystem, zcm_active=zcm_active)

        return filesystem
    return None


def zfs_clone(zfs_name, snapshot, parent=None, mountpoint=None, zcm_active=None):
    if not isinstance(zfs_name, str):
        log.error('The ZFS clone name must be provided')
    if not isinstance(snapshot, str):
        log.error('The ZFS snapshot must be provided')
    filesystem = zfs_name
    if parent is not None:
        filesystem = parent + '/' + zfs_name

    # Just debugging, don't fail if already created
    # if(destroy(filesystem, recursive=True) == 0):
    #    print('WARNING: Deleting filesystem (%s) ' % filesystem)

    options = []
    if mountpoint is not None:
        options.append('mountpoint=' + str(mountpoint))
    if zfs('clone', [snapshot, filesystem], options) == 0:
        # For watever reason, we can not add zfs_clone_manager:active property at creation time
        # We set this afterwards
        if zcm_active is not None:
            zfs_set(zfs_name, zcm_active=zcm_active)

        return filesystem

    return None


def zfs_set(zfs_name, readonly=None, mountpoint=None, mounted=None, zcm_path=None, zcm_active=None):
    result = 0
    if readonly is not None:
        option = 'readonly=' + ('on' if readonly else 'off')
        result |= zfs('set', [option, zfs_name])
    if mounted is not None:
        if mounted:
            result |= zfs('mount', [zfs_name])
        else:
            result |= zfs('unmount', [zfs_name])
    if mountpoint is not None:
        result |= zfs('set', ['mountpoint=' + str(mountpoint), zfs_name])
    if zcm_path is not None:
        result |= zfs(
            'set', ['zfs_clone_manager:path=' + str(zcm_path), zfs_name])
    if zcm_active is not None:
        option = 'zfs_clone_manager:active=' + ('on' if zcm_active else 'off')
        result |= zfs('set', [option, zfs_name])
    return result


def zfs_inherit(zfs_name, property_name):
    zfs('inherit', [property_name, zfs_name])


def value_convert(property_name, value):
    if value == 'on':
        return True
    if value == 'off':
        return False
    if value == '-':
        return None
    if property_name in ['mountpoint', 'zfs_clone_manager:path']:
        return pathlib.Path(value)
    try:
        return int(value)
    except ValueError:
        return value


def zfs_get(zfs_name, property_name):
    if property_name == 'all':
        raise NotImplementedError()
    cmd = ['/usr/sbin/zfs', 'get', '-Hp', property_name, zfs_name]
    with open('/dev/null', 'w') as dev_null:
        log.debug('Running command: "' + ' '.join(cmd) + '"')
        output = subprocess.check_output(cmd, stderr=dev_null)
        value = output.decode('utf-8').split('\t')[2]
        return value_convert(property_name, value)
    return None


def zfs_snapshot(zfs_name, filesystem, recursive=False):
    arguments = []
    if recursive:
        arguments.append('-r')
    snapshot = filesystem + '@' + zfs_name
    arguments.append(snapshot)
    if zfs('snapshot', arguments) == 0:
        return snapshot
    return None


def zfs_destroy(zfs_name, recursive=False, synchronous=True):
    arguments = []
    if recursive:
        arguments.append('-r')
    if synchronous:
        arguments.append('-s')
    arguments.append(zfs_name)
    return zfs('destroy', arguments)


def zfs_promote(zfs_name):
    return zfs('promote', [zfs_name])


def zfs_send(last_snapshot, target_file_path, first_snapshot=None, recursive=False):
    arguments = []
    if recursive:
        arguments.append('-R')
    if first_snapshot is not None:
        arguments += ['-I', first_snapshot]
    arguments.append(last_snapshot)
    with open(target_file_path, 'wb') as target_file:
        return _zfs('send', arguments, stdout=target_file)


def zfs_list(zfs_name=None, zfs_type=None, recursive=False,
             properties=['name', 'used', 'avail', 'refer', 'mountpoint']):
    cmd = ['/usr/sbin/zfs', 'list', '-Hp']
    if recursive:
        cmd.append('-r')
    if zfs_type is not None and zfs_type in ['all', 'filesystem',
                                             'snapshot', 'volume']:
        cmd += ['-t', zfs_type]
    if properties is not None:
        cmd += ['-o', ','.join(properties)]
    if zfs_name is not None:
        cmd.append(zfs_name)
    try:
        with open('/dev/null', 'w') as dev_null:
            filesystems = []
            log.debug('Running command: "' + ' '.join(cmd) + '"')
            output = subprocess.check_output(cmd, stderr=dev_null)
            for line in output.decode('utf-8').strip().split('\n'):
                values = line.split('\t')
                filesystem = {}
                for property_name, value in zip(properties, values):
                    filesystem[property_name] = value_convert(
                        property_name, value)
                filesystems.append(filesystem)
            return filesystems
    except:
        return []


def zfs_exists(zfs_name):
    filesystems = zfs_list(zfs_name, zfs_type='all', properties=['name'])
    return len(filesystems) == 1


def zfs_is_filesystem(zfs_name):
    try:
        return zfs_get(zfs_name, 'type') == 'filesystem'
    except:
        return False


def zfs_is_snapshot(zfs_name):
    try:
        return zfs_get(zfs_name, 'type') == 'snapshot'
    except:
        return False


def zfs_diff(final_snapshot, origin_snapshot=None, include_file_types=False, recursive=False):
    # Implemented as generator, in case it is too big
    file_types = {
        'F': 'file',
        '/': 'directory',
        'B': 'device',
        '>': 'door',
        '|': 'fifo',
        '@': 'link',
        'P': 'portal',
        '=': 'socket'
    }
    change_types = {
        '+': 'added',
        '-': 'removed',
        'M': 'modified',
        'R': 'renamed'
    }

    arguments = ['-H']
    if include_file_types:
        arguments.append('-F')
    if recursive:
        arguments.append('-r')
    if origin_snapshot is None:
        arguments.append('-E')
    else:
        arguments.append(origin_snapshot)
    arguments.append(final_snapshot)
    process = _zfs('diff', arguments, stdout=subprocess.PIPE)
    for line in io.TextIOWrapper(process.stdout, encoding="utf-8"):
        records = line.strip().split('\t')
        yield records


def zfs_rename(original_zfs_name, new_zfs_name):
    arguments = [original_zfs_name, new_zfs_name]
    return zfs('rename', arguments)
