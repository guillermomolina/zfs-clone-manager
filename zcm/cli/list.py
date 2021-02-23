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
import json

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
                                              description='List clones',
                                              help='List clones')
        parser.add_argument('-j', '--json',
                            action='store_true',
                            help='Output a JSON object')
        parser.add_argument('-T', '--no-trunc',
                            help='Don\'t truncate output',
                            action='store_true')
        parser.add_argument('-H', '--no-header',
                            help='Don\'t show header line(s)',
                            action='store_true')
        parser.add_argument('-P', '--page-size',
                            help='If list is longer than <page-size>, ask for more to continue in <page-size> intervals.\
                                Enter 0 to avoid pagination',
                            type=int,
                            default=25)
        parser.add_argument('path',
                            nargs='*',
                            metavar='filesystem|path',
                            help='zfs filesystem or path to show')

    def __init__(self, options):
        table = []
        managers = []
        if options.path:
            managers = [Manager(path) for path in options.path]
        else:
            managers = Manager.get_managers()
        if options.json:
            clones = []
            for manager in managers:
                for clone in manager.clones:
                    clones.append(clone.to_dictionary())
            print(json.dumps(clones, indent=4))
        else:
            for manager in managers:
                for clone in manager.clones:
                    table.append({
                        'manager': manager.zfs,
                        'a': '*' if manager.active_clone == clone else ' ',
                        'id': clone.id,
                        'clone': clone.zfs,
                        'mountpoint': str(clone.mountpoint),
                        'origin': clone.origin_id if clone.origin_id else '',
                        'date': clone.creation,
                        'size': format_bytes(clone.size)
                    })
            print_table(table, header=(not options.no_header), truncate=(
                not options.no_trunc), page_size=options.page_size)
