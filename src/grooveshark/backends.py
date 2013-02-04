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

import contextlib
import json

ASYNCHRONOUS = 0
SYNCHRONOUS = 1

try:
    import PySide.QtCore as QtCore
    import PySide.QtNetwork as QtNetwork
    pyside = True
except ImportError:
    pyside = None

try:
    import requests
except ImportError:
    requests = None
    
try:
    import urllib2 as urlib
except ImportError:
    import urllib.request as urllib
except ImportError:
    urllib = None

class GroovesharkError(Exception): pass
class RequestError(GroovesharkError): pass
class UnknownError(GroovesharkError): pass
class HTTPError(GroovesharkError): pass

class PySide():
    """
    Using PySide to access the API.
    """
    
    name = 'pyside'
    type = ASYNCHRONOUS
    available = pyside is not None
    
    def __init__(self, connection):
        self.connection = connection
        self.manager = QtNetwork.QNetworkAccessManager()

    def header(self, header, update, method, client, callback, secure):
        def call():
            header['token'] = self.connection.request_token(method, client)
            callback(header)
        if update:
            def new_token(token):
                self.connection.session.token = token
                call()
            self.connection.get_communication_token(new_token, secure)
        else:
            call()
    
    def request(self, protocol, url, data, headers, callback, secure):
        url = QtCore.QUrl(url)
        request = QtNetwork.QNetworkRequest(url)
        for key, value in headers.items():
            request.setRawHeader(key, value)
        data = QtCore.QByteArray(data)
        reply = self.manager.post(request, data)
        def call():
            data = reply.readData(reply.bytesAvailable())
            result = json.loads(str(data))
            if 'result' in result:
                callback(result['result'])
            elif 'fault' in result:
                callback(RequestError(result['fault']['message'],
                                      result['fault']['code']))
            else:
                callback(UnknownError(result))
        reply.finished.connect(call)                

class Requests():
    """
    Using Requests to access the API.
    """
    
    name = 'requests'
    type = SYNCHRONOUS
    available = requests is not None
    
    def __init__(self, connection):
        self.connection = connection
    
    def header(self, header, update, method, client, callback, secure):
        if update:
            self.connection.session.token = \
            self.connection.get_communication_token(None, secure)
        header['token'] = self.connection.request_token(method, client)
        return header
    
    def request(self, protocol, url, data, headers, callback, secure):
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if 'result' in result:
                return result['result']
            elif 'fault' in result:
                raise RequestError(result['fault']['message'],
                                   result['fault']['code'])
            else:
                raise UnknownError(result)
        else:
            raise HTTPError(response.status_code)
    
class Urllib():
    """
    Using Urllib to access the API.
    """
    
    name = 'urllib'
    type = SYNCHRONOUS
    available = urllib is not None
    
    def __init__(self, connection):
        self.connection = connection
        proxy_handler = urllib.ProxyHandler(self.connection.proxies)
        self.urlopen = urllib.build_opener(proxy_handler).open
    
    def header(self, header, update, method, client, callback, secure):
        if update:
            self.connection.session.token = \
            self.connection.get_communication_token(None, secure)
        header['token'] = self.connection.request_token(method, client)
        return header
    
    def request(self, protocol, url, data, headers, callback, secure):
        request = urllib.Request(url, data=data, headers=headers)
        try:
            with contextlib.closing(self.urlopen(request)) as response:
                result = json.loads(response.read().decode('utf-8'))
                if 'result' in result:
                    return result['result']
                elif 'fault' in result:
                    raise RequestError(result['fault']['message'],
                                       result['fault']['code'])
                else:
                    raise UnknownError(result)
        except urllib.HTTPError as response:
            raise HTTPError(response.getcode())