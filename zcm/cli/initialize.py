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


class Initialize:
    name = 'initialize'
    aliases = ['init']

    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser(Initialize.name,
                                              parents=[parent_parser],
                                              aliases=Initialize.aliases,
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='Init ZCM on specified ZFS',
                                              help='Init ZCM on specified ZFS')
        parser.add_argument('zfs',
                            metavar='filesystem',
                            help='root ZFS filesystem')
        parser.add_argument('path',
                            help='root path')

    def __init__(self, options):
        Manager.initialize_zfs(options.zfs, options.path)
        if not options.quiet:
            print('ZCM initialized ZFS %s at path %s' %
                  (options.zfs, options.path))
