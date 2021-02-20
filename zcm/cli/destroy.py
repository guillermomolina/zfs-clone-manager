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


import argparse

from zcm.api.manager import Manager


def are_you_sure(force, manager):
    if force:
        return True
    print('WARNING!!!!!!!!')
    print('All the filesystems, clones, snapshots and directories associated with %s will be permanently deleted.' % manager.zfs)
    print('This operation is not reversible.')
    answer = input('Do you want to proceed? (yes/NO) ')
    return answer == 'yes'


class Destroy:
    name = 'destroy'
    aliases = []

    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser(Destroy.name,
                                              parents=[parent_parser],
                                              aliases=Destroy.aliases,
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='Destroy ZCM on path',
                                              help='Remove all ZCM metadata (filesystems, clones, snapshots and directories) associated with path')
        parser.add_argument('--force',
                            help='Force destroy without confirmation',
                            action='store_true')
        parser.add_argument('path',
                            metavar='filesystem|path',
                            nargs='+',
                            help='zfs filesystem or path of ZCM')

    def __init__(self, options):
        managers = [ Manager(path) for path in options.path ]
        for manager in managers:
            if are_you_sure(options.force, manager):
                manager.destroy()
                if not options.quiet:
                    print('Destroyed ZCM %s' % manager.zfs)
