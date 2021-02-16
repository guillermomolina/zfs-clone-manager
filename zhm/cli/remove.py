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
import logging
from zhm import ZHMError
from zhm.exceptions import ZHMException
from zhm.api.manager import Manager

log = logging.getLogger(__name__)


class Remove:
    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser('rm',
                                              parents=[parent_parser],
                                              aliases=['remove'],
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='Remove one or more instances',
                                              help='Remove one or more instances')
        parser.add_argument('id',
                            nargs='+',
                            help='ID of the instance to remove')

    def __init__(self, options):
        manager = Manager(options.path)
        for id in options.id:
            manager.remove(id)
            if not options.quiet:
                print('Removed instance ' + id)
