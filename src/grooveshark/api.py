# -*- coding:utf-8 -*-
#
# Copyright (C) 2013, Maximilian Köhl <linuxmaxi@googlemail.com>
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
# along with this program. If not, see <http://www.gnu.org/licenses/>

from __future__ import unicode_literals, division

import hashlib
import json
import pickle
import random
import time
import uuid

from grooveshark.backends import Urllib
from grooveshark.clients import JSQueue, HTMLShark
from grooveshark.constants import Constants

class Session():
    def __init__(self, connection):
        self.connection = connection
        self.uuid = str(uuid.uuid4()).upper()
        self.id = hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest()
        self.secret = hashlib.md5(self.id.encode('utf-8')).hexdigest()
        self.country = self.connection.constants.country
        self.queue = None
        self.last = 0
        self.username = None
        self.password = None
        self.authenticated = False
        self.userid = 0
        self._token = None
    
    @property
    def token(self):
        return self._token
    
    @token.setter
    def token(self, token):
        self._token = token
        self._last = time.time()
    
    def save(self, filename):
        with open(filename, 'wb') as session:
            pickle.dump([self.uuid, self.id, self.secret, self.country,
                         self.queue, self.last, self.username, self.password,
                         self.authenticated, self.userid, self._token], session)
    
    def open(self, filename):
        with open(filename, 'rb') as session:
            (self.uuid, self.id, self.secret, self.country, self.queue,
             self.last, self.username, self.password, self.authenticated,
             self.userid, self._token) = pickle.load(session)

class Connection():
    def __init__(self, proxies={}, backend=Urllib, constants=Constants):
        self.proxies = proxies
        self.constants = constants
        self.session = Session(self)
        self.backend = backend(self)        
    
    def _random_hex(self):
        return ''.join([random.choice('0123456789abcdef') for i in range(6)])
        
    def request_token(self, method, client):
        random_value = self._random_hex()
        return random_value + hashlib.sha1((method + ':' + self.session.token +
                                            ':' + client.secret + ':' +
                                            random_value
                                            ).encode('utf-8')).hexdigest()
    
    def get_communication_token(self, callback=None, secure=True):
        return self.request('getCommunicationToken',
                            {'secretKey' : self.session.secret},
                            {'uuid' :self.session.uuid,
                             'session' : self.session.id,
                             'clientRevision' : HTMLShark.version,
                             'country' : self.session.country,
                             'privacy' : 0,
                             'client' : HTMLShark.name}, callback, secure)
    
    def header(self, method, client=HTMLShark, callback=None, secure=True):
        header = {'privacy' : 0, 'uuid' : self.session.uuid,
                  'clientRevision' : client.version,
                  'session' : self.session.id, 'client' : client.name,
                  'country' : self.session.country}
        header.update(client.header)
        update = time.time() - self.session.last > self.constants.token_timeout
        return self.backend.header(header, update, method, client, callback,
                                   secure)
    
    def request(self, method, parameters, header, callback=None, secure=True):
        protocol = 'https' if secure else 'http'
        url = '{}://grooveshark.com/more.php?{}'.format(protocol, method)
        data = json.dumps({'parameters' : parameters,
                           'method' : method,
                           'header' : header}).encode('utf-8')      
        headers = {'Cookie' : 'PHPSESSID=' + self.session.id,
                   'User-Agent' : self.constants.user_agent,
                   'Content-Type' : 'application/json'}
        return self.backend.request(protocol, url, data, headers, callback,
                                    secure)

class Client():
    pass