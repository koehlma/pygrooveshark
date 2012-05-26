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
from grooveshark.core.session import Session

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
    def __init__(self, session=None, proxies=None):
        self.session = Session() if session is None else session
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
        return {'Cookie' : 'PHPSESSID=' + self.session.session, 'Content-Type' : 'application/json',
                'User-Agent' : USER_AGENT, 'Content-Type' : 'application/json'}
    
    def _get_token(self):
        '''
        Requests an communication token from grooveshark.
        '''
        self.session.token = self.request('getCommunicationToken', {'secretKey' : self.session.secret},
                                          {'uuid' :self.session.user,
                                           'session' : self.session.session,
                                           'clientRevision' : CLIENTS['htmlshark']['version'],
                                           'country' : self.session.country,
                                           'privacy' : 0,
                                           'client' : 'htmlshark'})[1]
        self.session.time = time.time()
    
    def _request_token(self, method, client):
        '''
        Generates a request token.
        '''
        if time.time() - self.session.time > TOKEN_TIMEOUT:
            self._get_token()
        random_value = self._random_hex()
        return random_value + hashlib.sha1((method + ':' + self.session.token + ':' + CLIENTS[client]['token'] + ':' + random_value).encode('utf-8')).hexdigest()
    
    def init(self):
        '''
        Initiate session, token and queue.
        '''
        return self.init_token(), self.init_queue()
        
    def init_token(self):
        '''
        Initiate token.
        '''
        self._get_token()
    
    def init_queue(self):
        '''
        Request queue id.
        '''
        self.session.queue = self.request('initiateQueue', None, self.header('initiateQueue', 'jsqueue'))[1]
    
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
                'uuid' : self.session.user,
                'clientRevision' : CLIENTS[client]['version'],
                'session' : self.session.session,
                'client' : client,
                'country' : self.session.country}