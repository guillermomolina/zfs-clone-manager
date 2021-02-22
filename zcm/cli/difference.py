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
from zcm.lib.print import print_table
from zcm.lib.zfs import zfs_diff


class Difference:
    name = 'difference'
    aliases = ['diff']

    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser(Difference.name,
                                              parents=[parent_parser],
                                              aliases=Difference.aliases,
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='Gives a high-level description of the differences between\
                                                  a clone and its origin',
                                              help='Differencies between a clone and its origin')
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
                            metavar='filesystem|path',
                            help='zfs filesystem or path of ZCM')
        parser.add_argument('id',
                            nargs='?',
                            help='clone id',
                            default='active')

    def __init__(self, options):
        manager = Manager(options.path)
        id = manager.active_clone.id if options.id == 'active' else options.id
        clone = manager.get_clone(id)
        table = zfs_diff(clone.zfs, clone.origin, include_file_types=True)
        print_table(table, header=(not options.no_header), truncate=(
            not options.no_trunc), page_size=options.page_size)
