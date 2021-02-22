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
import random
import string


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
