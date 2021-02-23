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

import json
import logging

log = logging.getLogger(__name__)

class Clone:
    def __init__(self, id, zfs, origin, origin_id, mountpoint, creation, size):
        self.id = id
        self.zfs = zfs
        self.origin = origin
        self.origin_id = origin_id
        self.mountpoint = mountpoint
        self.creation = creation
        self.size = size
    
    def to_json(self):
        data = self.__dict__.copy()
        data['mountpoint'] = str(self.mountpoint)
        data['creation'] = str(self.creation)

        return json.dumps(data, indent=4)
       
