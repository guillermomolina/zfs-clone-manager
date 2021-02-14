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
import importlib
import logging
from zhm import __version__
from zhm import zhm_config
from zhm.cli.initialize import Initialize
from zhm.cli.list import List
from zhm.cli.create import Create
from zhm.cli.activate import Activate
from zhm.cli.remove import Remove
from zhm.exceptions import ZHMException
from pathlib import Path

log = logging.getLogger(__name__)


def set_log_level(log_level):
    if log_level == 'none':
        logging.disable(logging.CRITICAL)
    else:
        levels = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warn': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        logging.basicConfig(level=levels[log_level])


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                      argparse.RawDescriptionHelpFormatter):
    pass


class CLI:
    commands = {
        'init': Initialize,
        'ls': List,
        'create': Create,
        'activate': Activate,
        'rm': Remove
    }

    def __init__(self):
        parser = argparse.ArgumentParser(
            formatter_class=CustomFormatter,
            description='A self-sufficient history for containers')
        parser.add_argument('-V', '--version',
                            help='Print version information and quit',
                            action='version',
                            version='%(prog)s version ' + __version__)
        parser.add_argument('-l', '--log-level',
                            help='Set the logging level ("debug"|"info"|"warn"|"error"|"fatal")',
                            choices=[
                                'debug',
                                'info',
                                'warn',
                                'error',
                                'critical',
                                'none'
                            ],
                            metavar='LOG_LEVEL',
                            default='none')
        parser.add_argument('-D', '--debug',
                            help='Enable debug mode',
                            action='store_true')
        parser.add_argument('-p', '--path',
                            help='path to manage')

        subparsers = parser.add_subparsers(
            dest='command',
            metavar='COMMAND',
            required=True)

        for command in CLI.commands.values():
            command.init_parser(subparsers)

        options = parser.parse_args()

        set_log_level(options.log_level)

        if options.debug:
            import debugpy
            debugpy.listen(('0.0.0.0', 5678))
            log.info("Waiting for IDE to attach...")
            debugpy.wait_for_client()

        if not options.path:
            options.path = Path.cwd().as_posix()

        try:
            command = CLI.commands[options.command]
            command(options)
        except ZHMException as e:
            log.error(e.message)
            print(e.message)
            exit(-1)


def main():
    CLI()


if __name__ == '__main__':
    main()
