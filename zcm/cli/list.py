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
from datetime import datetime

from zcm.api.manager import Manager
from zcm.lib.print import format_bytes, print_table


class List:
    name = 'list'
    aliases = ['ls']

    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser(List.name,
                                              parents=[parent_parser],
                                              aliases=List.aliases,
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='List hosts',
                                              help='List hosts')
        parser.add_argument('--no-trunc',
                            help='Don\'t truncate output',
                            action='store_true')
        parser.add_argument('path',
                            nargs='*',
                            metavar='filesystem|path',
                            help='zfs filesystem or path to show')

    def __init__(self, options):
        table = []
        managers = []
        if options.path:
            managers = [ Manager(path) for path in options.path ]
        else:
            managers = Manager.get_managers()
        for manager in managers:
            for clone in manager.clones:
                table.append({
                    'manager': manager.zfs,
                    'a': '*' if manager.active_clone == clone else ' ',
                    'id': clone.id,
                    'clone': clone.zfs,
                    'mountpoint': clone.mountpoint,
                    'origin': clone.origin_id if clone.origin_id else '',
                    'date': datetime.fromtimestamp(clone.creation),
                    'size': format_bytes(clone.size)
                })
        print_table(table, truncate=(not options.no_trunc))
