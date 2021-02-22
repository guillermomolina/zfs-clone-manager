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

from collections import deque
from itertools import islice

from zcm import zcm_config

# TODO: use from prettytable import PrettyTable ?

def print_table(table, header=True, truncate=True, separation=2, identation=0, page_size=25):
    if page_size <= 0:
        page_size = None
    i = iter(table)
    ask_for_more = False
    while True:
        page = tuple(islice(i, 0, page_size))
        if len(page):
            if ask_for_more:
                answer = input('Do you want to see more? (Y/n) ')
                if answer and answer.upper()[0] == 'N':
                    return
            print_table_page(page, header, truncate, separation, identation)
            ask_for_more = True
        else:
            return


def print_table_page(page, header=True, truncate=True, separation=2, identation=0):
    MAX_COLUMN_LENGTH = zcm_config['max_column_length']
    if len(page) == 0:
        return

    columns = []
    # initialize columns from first row's keys
    for key in page[0]:
        columns.append({
            'key': key,
            'tittle': key.upper(),
            'length': len(key)
        })

    # adjust columns lenghts to max record sizes
    for column in columns:
        for row in page:
            value = str(row[column['key']]).replace('\t', ' ')
            row[column['key']] = value
            column['length'] = max(column['length'], len(value))

    if truncate:
        for column in columns:
            column['length'] = min(column['length'], MAX_COLUMN_LENGTH)

    separation_string = ' ' * separation

    # print headers
    if header:
        strings = [''] * identation if identation > 0 else []
        for column in columns:
            str_format = '{:%s}' % str(column['length'])
            strings.append(str_format.format(column['tittle']))
        print(separation_string.join(strings))

    for row in page:
        strings = [''] * identation if identation > 0 else []
        for column in columns:
            value = row[column['key']]
            if truncate and len(value) > MAX_COLUMN_LENGTH:
                value = value[:MAX_COLUMN_LENGTH-3] + '...'
            str_format = '{:%s}' % str(column['length'])
            strings.append(str_format.format(value))
        print(separation_string.join(strings))

def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB', 5: 'PB'}
    while size > power:
        size /= power
        n += 1
    return '{:.2f} {:s}'.format(size, power_labels[n])


def print_info(data):
    for key, value in data.items():
        print('%s: %s' % (key, value))
