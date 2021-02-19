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


def are_you_sure(force, id):
    if force:
        return True
    print('WARNING!!!!!!!!')
    print('All the filesystems, snapshots and directories associated with clone %s will be permanently deleted.' % id)
    print('This operation is not reversible.')
    answer = input('Do you want to proceed? (yes/NO) ')
    return answer == 'yes'


class Remove:
    name = 'remove'
    aliases = ['rm']

    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser(Remove.name,
                                              parents=[parent_parser],
                                              aliases=Remove.aliases,
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='Remove one or more clones',
                                              help='Remove one or more clones')
        parser.add_argument('--force',
                            help='Force remove clone without confirmation',
                            action='store_true')
        parser.add_argument('path',
                            metavar='filesystem|path',
                            help='zfs filesystem or path of ZCM')
        parser.add_argument('id',
                            nargs='+',
                            help='ID of the clone to remove')

    def __init__(self, options):
        manager = Manager(options.path)
        for id in options.id:
            if are_you_sure(options.force, id):
                manager.remove(id)
                if not options.quiet:
                    print('Removed clone ' + id)
