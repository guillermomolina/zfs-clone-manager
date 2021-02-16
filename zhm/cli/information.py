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

from zhm.api import Manager
from zhm.api.print import print_info


class Information:

    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser('info',
                                              parents=[parent_parser],
                                              aliases=['information'],
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='Show ZHM information',
                                              help='Show ZHM information')
        parser.add_argument('-P', '--parseable',
                            help='Show parseable info',
                            action='store_true')

    def __init__(self, options):
        manager = Manager(options.path)
        data = {
            'Path': manager.path,
            'Root ZFS': manager.zfs,
            'Used bytes': manager.used,
            'Clone count': len(manager.instances),
            'Oldest clone ID': manager.instances[0]['id'],
            'Active clone ID': manager.active['id'],
            'Newest clone ID': manager.instances[-1]['id'],
            'Next clone ID': manager.next_id
        }
        if options.parseable:
            print_info(data)
        else:
            print_info(data)
