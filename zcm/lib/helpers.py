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
import random
import string
import subprocess

log = logging.getLogger(__name__)


def check_positive(value, min_value=0):
    ivalue = int(value)
    if ivalue < min_value:
        raise argparse.ArgumentTypeError(
            "%s is an invalid positive int value" % value)
    return ivalue


def check_one_or_more(value):
    return check_positive(value, 1)


# https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# shutil.copytree does not copy owner
def copy_directory(source, target):
    if not source.is_dir() or not target.is_dir():
        return -1
    cmd1 = ['tar', 'cf', '-', '.']
    cmd2 = ['tar', 'xf', '-']
    log.debug('Running command: "cd %s; %s | (cd %s; %s)"' % (str(source), ' '.join(cmd1), str(target), ' '.join(cmd2)))
    process1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE, cwd=source)
    process2 = subprocess.Popen(cmd2, stdin=process1.stdout, cwd=target)
    process1.stdout.close()
    stdout, stderr = process2.communicate()
    if stdout:
        for line in iter(stdout.splitlines()):
            log.info(line)
    if stderr:
        for line in iter(stderr.splitlines()):
            if process2.returncode == 0:
                log.warning(line)
            else:
                log.error(line)
    return process2.returncode
