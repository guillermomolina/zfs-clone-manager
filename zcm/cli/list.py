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

from zcm.api import Manager
from zcm.lib.print import format_bytes, print_table


class List:

    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser('ls',
                                              parents=[parent_parser],
                                              aliases=['list'],
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='List hosts',
                                              help='List hosts')
        parser.add_argument('--no-trunc',
                            help='Don\'t truncate output',
                            action='store_true')

    def __init__(self, options):
        manager = Manager(options.path)
        table = []
        for clone in manager.clones:
            table.append({
                'a': '*' if manager.active == clone else ' ',
                'id': clone['id'],
                'mountpoint': clone['mountpoint'],
                'origin': clone['origin_id'] if clone['origin_id'] else '',
                'date': datetime.fromtimestamp(clone['creation']),
                'size': format_bytes(clone['used'])
            })
        print_table(table, truncate=(not options.no_trunc))