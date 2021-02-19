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

from zcm.api import Manager
from zcm.lib.print import format_bytes, print_info, print_table


class Information:
    name = 'information'
    aliases = ['info']

    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser(Information.name,
                                              parents=[parent_parser],
                                              aliases=Information.aliases,
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='Show ZCM information',
                                              help='Show ZCM information')
        parser.add_argument('-t', '--table',
                            help='Show information as table',
                            action='store_true')
        parser.add_argument('path',
                            nargs='*',
                            metavar='filesystem|path',
                            help='zfs filesystem or path to show')

    def __init__(self, options):
        managers = []
        if options.path:
            managers = [ Manager(path) for path in options.path ]
        else:
            managers = Manager.get_managers()
        if options.table:
            table = []
            for manager in managers:
                table.append({
                    'path': manager.path,
                    'zfs': manager.zfs,
                    'size': format_bytes(manager.size),
                    'total': len(manager.clones),
                    'older': len(manager.older_clones),
                    'newer': len(manager.newer_clones),
                    'oldest_id': manager.clones[0].id,
                    'active_id': manager.active_clone.id,
                    'newest_id': manager.clones[-1].id,
                    'next_id': manager.next_id
                })
            print_table(table)
        else:
            for manager in managers:
                data = {
                    'Path': manager.path,
                    'Root ZFS': manager.zfs,
                    'Root ZFS size': format_bytes(manager.size),
                    'Total clone count': len(manager.clones),
                    'Older clone count': len(manager.older_clones),
                    'Newer clone count': len(manager.newer_clones),
                    'Oldest clone ID': manager.clones[0].id,
                    'Active clone ID': manager.active_clone.id,
                    'Newest clone ID': manager.clones[-1].id,
                    'Next clone ID': manager.next_id
                }
                print_info(data)
                print()
