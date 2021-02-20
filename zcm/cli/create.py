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
from zcm.lib.helpers import check_one_or_more


class Create:
    name = 'create'
    aliases = []

    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser(Create.name,
                                              parents=[parent_parser],
                                              aliases=Create.aliases,
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='Create a new clone',
                                              help='Create a new clone')
        parser.add_argument('-m', '--max-newer',
                            type=check_one_or_more,
                            help='Do not create if there are <max-newer> newer clones')
        parser.add_argument('-t', '--max-total',
                            type=check_one_or_more,
                            help='Do not create if there are <max-total> clones')
        parser.add_argument('-a', '--auto-remove',
                            action='store_true',
                            help='Remove clones if maximum limits excedeed')
        parser.add_argument('path',
                            metavar='filesystem|path',
                            help='zfs filesystem or path of ZCM')

    def __init__(self, options):
        manager = Manager(options.path)
        clone = manager.create(
            options.max_newer, options.max_total, options.auto_remove)
        if not options.quiet:
            print('Created clone %s at path %s' %
                  (clone.id, clone.mountpoint))
