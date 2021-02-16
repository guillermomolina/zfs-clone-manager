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

from zhm.api.manager import Manager


class Clone:
    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser('clone',
            parents=[parent_parser],
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Clone a new instance',
            help='Clone a new instance')
 
    def __init__(self, options):
        manager = Manager(options.path)
        instance = manager.clone()
        if not options.quiet:
            print('Created instance %s at path %s' % (instance['id'], instance['mountpoint']))
