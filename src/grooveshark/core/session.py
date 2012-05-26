# -*- coding:utf-8 -*-
#
# Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import hashlib
import pickle
import uuid

class Session():
    def __init__(self):
        self.user = str(uuid.uuid4())
        self.session = hashlib.md5(self.user.encode('utf-8')).hexdigest()
        self.secret = hashlib.md5(self.session.encode('utf-8')).hexdigest()
        self.country = {'ID': 221, 'CC1': 0, 'CC2': 0, 'CC3': 0, 'CC4': 0, 'DMA': 0, 'IPR': 0}
        self.queue = None
        self.token = None
        self.time = None
    
    def __repr__(self):
        return '<Session user="{}", sessions="{}", secret="{}", country="{}">'.format(self.user, self.session, self.secret, self.country)
    
    @classmethod
    def open(cls, filename):
        with open(filename, 'rb') as input:
            return pickle.load(input)
    
    def save(self, filename):
        with open(filename, 'wb') as output:
            pickle.dump(self, output)