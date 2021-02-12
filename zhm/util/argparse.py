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

def get_subparser_aliases(parser, commands):
    dest = 'subcommand'
    out = {}
    prog_str = parser.prog
    dest_dict = {a.dest: a for a in parser._actions}
    try:
        choices = dest_dict.get(dest).choices
    except AttributeError:
        raise AttributeError(f'The parser "{parser}" has no subparser with a `dest` of "{dest}"')

    for k, v in choices.items():
        clean_v = v.prog.replace(prog_str, '', 1).strip()
        out[k] = commands[clean_v]
    
    return out
