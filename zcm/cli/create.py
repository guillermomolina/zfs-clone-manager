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


class create:
    name = 'create'
    aliases = []

    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser(create.name,
                                              parents=[parent_parser],
                                              aliases=create.aliases,
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='Create ZCM on specified ZFS',
                                              help='Create ZCM on specified ZFS')
        parser.add_argument('zfs',
                            metavar='filesystem',
                            help='root ZFS filesystem')
        parser.add_argument('path',
                            help='root path')

    def __init__(self, options):
        Manager.create_manager(options.zfs, options.path)
        if not options.quiet:
            print('ZCM created with ZFS %s at path %s' %
                  (options.zfs, options.path))
