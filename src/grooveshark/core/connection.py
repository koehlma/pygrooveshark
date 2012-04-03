# -*- coding:utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

import contextlib
import json
import time
import hashlib

if sys.version[0] == '3':
    import urllib.request as urllib
else:
    import urllib2 as urllib
        
import uuid
import random
import re

from grooveshark.core.const import *

class RequestError(Exception):
    '''
    Some grooveshark api specified error occur during request.
    '''
    
class UnknownError(Exception):
    '''
    Some unspecified error ccur during request. 
    '''

class Connection():
    '''
    Lowlevel api communication.
    
    :param session: stored session information as returned by :meth:`init_session` method.
    :param token: stored token information as returned by :meth:`init_token` method.
    :param queue_id: stored queue id as returned by :meth:`init_queue` method.
    :param proxies: dictionary mapping protocol to proxy.
    '''
    def __init__(self, session=None, token=None, queue_id=None, proxies=None):
        if session:
            self._session = session[0]
            self._secret = session[1]
            self.country = session[2]
            self._user = session[3]
        if token:
            self._token = token[0]
            self._token_time = token[1]
        if queue_id:
            self.queue_id = queue_id
        self.urlopen = urllib.build_opener(urllib.ProxyHandler(proxies)).open
    
    def _random_hex(self):
        '''
        Generates a random hex string.
        '''
        hex_set = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        return ''.join([random.choice(hex_set) for i in range(6)])
    
    def _json_request_header(self):
        '''
        Generates json http request headers.
        '''
        return {'Cookie' : 'PHPSESSID=' + self._session, 'Content-Type' : 'application/json',
                'User-Agent' : USER_AGENT,
                'Content-Type' : 'application/json'}
    
    def _get_token(self):
        '''
        Requests an communication token from grooveshark.
        '''
        self._token = self.request('getCommunicationToken', {'secretKey' : self._secret},
                                   {'uuid' :self._user,
                                    'session' : self._session,
                                    'clientRevision' : CLIENTS['htmlshark']['version'],
                                    'country' : self.country,
                                    'privacy' : 0,
                                    'client' : 'htmlshark'})[1]
        self._token_time = time.time()
    
    def _request_token(self, method, client):
        '''
        Generates a request token.
        '''
        if time.time() - self._token_time > TOKEN_TIMEOUT:
            self._get_token()
        random_value = self._random_hex()
        return random_value + hashlib.sha1((method + ':' + self._token + ':' + CLIENTS[client]['token'] + ':' + random_value).encode('utf-8')).hexdigest()
    
    def init(self, old_way=False):
        '''
        Initiate session, token and queue.
        '''
        return self.init_session(old_way), self.init_token(), self.init_queue()
    
    def init_session(self, old_way=False):
        '''
        Initiate session.
        '''
        if old_way:
            request = urllib.Request('http://www.grooveshark.com/', headers={'User-Agent' : USER_AGENT})
            response = self.urlopen(request)
            self._session = re.search('PHPSESSID=([a-z0-9]*)', response.info()['Set-Cookie']).group(1)
            self._secret = hashlib.md5(self._session.encode('utf-8')).hexdigest()
            self.country = json.loads(re.search(r'\<script type="text/javascript"\>window\.gsConfig = (\{.*\});\<\/script\>',
                                                 response.read().decode('utf-8')).group(1))['country']
        else:
            self._session = hashlib.md5(str(random.randint(0, 99999999999999999)).encode('utf-8')).hexdigest()
            self._secret = hashlib.md5(self._session.encode('utf-8')).hexdigest()
            self.country = COUNTRY
        self._user = str(uuid.uuid4()).upper()
        return self._session, self._secret, self.country, self._user
    
    def init_token(self):
        '''
        Initiate token.
        '''
        self._get_token()
        return self._token, self._token_time
    
    def init_queue(self):
        '''
        Request queue id.
        '''
        self.queue_id = self.request('initiateQueue', None, self.header('initiateQueue', 'jsqueue'))[1]
        return self.queue_id
    
    def request(self, method, parameters, header):
        '''
        Grooveshark api request.
        '''
        data = json.dumps({'parameters' : parameters, 'method' : method, 'header' : header})
        request = urllib.Request('https://grooveshark.com/more.php?%s' % (method),
                                         data=data.encode('utf-8'), headers=self._json_request_header())
        with contextlib.closing(self.urlopen(request)) as response:
            result = json.loads(response.read().decode('utf-8'))
            if 'result' in result:
                return response.info(), result['result']
            elif 'fault' in result:
                raise RequestError(result['fault']['message'], result['fault']['code'])
            else:
                raise UnknownError(result)
    
    def header(self, method, client='htmlshark'):
        '''
        Generates Grooveshark api json header.
        ''' 
        return {'token' : self._request_token(method, client),
                'privacy' : 0,
                'uuid' : self._user,
                'clientRevision' : CLIENTS[client]['version'],
                'session' : self._session,
                'client' : client,
                'country' : self.country}