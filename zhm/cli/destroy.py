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
from zhm.api.manager import Manager

log = logging.getLogger(__name__)

def are_you_sure(force, path):
    if force: 
        return True
    print('WARNING!!!!!!!!')
    print('All the filesystems, clones, snapshots and directories associated with %s will be permanently deleted.' % path)
    print('This operation is not reversible.')
    answer = input('Do you want to proceed? (yes/NO) ')
    return answer == 'yes'

class Destroy:
    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser('destroy',
                                              parents=[parent_parser],
                                              formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                              description='Destroy ZHM on path',
                                              help='Remove all ZHM metadata (filesystems, clones, snapshots and directories) associated with path')
        parser.add_argument('--force',
                            help='Force destroy without confirmation',
                            action='store_true')

    def __init__(self, options):
        manager = Manager(options.path)
        if are_you_sure(options.force, options.path):
            manager.destroy()
            print('Destroyed ZHM at path %s' % options.path)
