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


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

class Clone:
    @staticmethod
    def init_parser(parent_subparsers):
        parent_parser = argparse.ArgumentParser(add_help=False)
        parser = parent_subparsers.add_parser('clone',
            parents=[parent_parser],
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Clone a new clone',
            help='Clone a new clone')
        parser.add_argument('-m', '--max-newer',
                            type=check_positive,
                            help='Do not clone if there are <max-newer> newer clones')
        parser.add_argument('-t', '--max-total',
                            type=check_positive,
                            help='Do not clone if there are <max-total> clones')
 
    def __init__(self, options):
        manager = Manager(options.path)
        clone = manager.clone(options.max_newer, options.max_total)
        if not options.quiet:
            print('Created clone %s at path %s' % (clone['id'], clone['mountpoint']))
