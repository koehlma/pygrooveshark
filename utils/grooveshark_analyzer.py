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

"""
This tool provides a Grooveshark analyzer. Basically it is a proxy for the API
endpoint `*grooveshark.com/more.php*`. It displays all sniffed information
nicely formatted and maintains an internal state of the API. Per request it
displays:
    * session id
    * current communication token
    * request method
    * request client (htmlshark or jsqueue)
    * the `uuid` of the session
    * the `country` of the session
    * request token
    * request parameters
    * request result
The sniffed data can than be used by `grooveshark_get_secret.py` to extract the
security tokens out of a memory dump.

To sniff the SSL encrypted API endpoint it uses it's own SSL certificates - you
have to add these certificates to the list of trusted exceptions.

Run this tool and configure FoxyProxy (Firefox AddOn) to route all requests to
`*grooveshark.com/more.php*` through this proxy. Per default it listens on
`127.0.0.1:12345`.
"""

__version__ = '1.0'

import argparse
import gzip
import http.cookies
import http.server
import json
import os
import socketserver
import ssl
import threading
import urllib.request
import urllib.parse
import zlib

__path__ = os.path.dirname(__file__)

# load the ssl certificate and the private key
SSL_KEY = os.path.join(__path__, 'certs', 'server.key')
SSL_CERT = os.path.join(__path__, 'certs', 'server.crt')

class Proxy(http.server.BaseHTTPRequestHandler):
    def __init__(self, connection, client_address, server, ssl=False):
        self.ssl = ssl
        super().__init__(connection, client_address, server)
    
    def _grooveshark(self):
        # parse cookies to extract the session id
        cookies = http.cookies.SimpleCookie(self.headers['Cookie'])
        session = cookies['PHPSESSID'].value
        # read and parse the json api request
        data = self.rfile.read(int(self.headers['Content-Length']))
        api_request = json.loads(data.decode('utf-8'))
        # build and open a new request to the real api
        request = urllib.request.Request(self.path, data, self.headers)
        request.get_method = lambda: self.command
        try:
            response = urllib.request.urlopen(request)
        except urllib.request.URLError as error:
            response = error
        # redirect http status code and message
        self.send_response(response.getcode(), response.msg)
        # redirect http headers
        for key, value in response.headers.items():
            self.send_header(key, value)
        self.end_headers()
        # redirect the json result
        data = response.read()
        self.wfile.write(data)
        # decompress the result
        if response.headers['Content-Encoding'] == 'deflate':
            data = zlib.decompress(data)
        elif response.headers['Content-Encoding'] == 'gzip':
            data = gzip.decompress(data)
        # parse the json result into a python dictionary
        api_response = json.loads(data.decode('utf-8'))
        # check if the session already exists
        if session not in self.server.sessions:
            # create the new session
            self.server.sessions[session] = {'token' : None}
        # store the sessions communication token
        if api_request['method'] == 'getCommunicationToken':
            self.server.sessions[session]['token'] = api_response['result']
        if self.server.methods is not None:
            # check for a new method and display method information
            if api_request['method'] not in self.server.methods:
                with server.lock:
                    self.server.methods.append(api_request['method'])
                    print('--> New Method "{}":'.format(api_request['method']))
                    print(('    --> Client: "{}"'
                           ).format(api_request['header']['client']))
                    print(('    --> Parameters: "{}"'
                           ).format(('", "'
                                     ).join(api_request['parameters'].keys())))
        else:
            # display request information
            with server.lock:
                print('--> Session "{}":'.format(session))
                print(('    --> Communication Token: {}'
                       ).format(self.server.sessions[session]['token']))
                print('    --> Method: {}'.format(api_request['method']))
                print(('    --> Client: {}/{}')
                      .format(api_request['header']['client'],
                              api_request['header']['clientRevision']))
                print('    --> UUID: {}'.format(api_request['header']['uuid']))
                print(('    --> Country: "{}"'
                       ).format(api_request['header']['country']))
                print(('    --> Token: {}'
                       ).format(api_request['header']['token']))
                print('    --> Parameters:')
                for key, value in api_request['parameters'].items():
                    print('        --> "{}" : "{}"'.format(key,
                                                           str(value)[:80]))
                print('    --> Result:')
                if isinstance(api_response['result'], dict):
                    for key, value in api_response['result'].items():
                        print('        --> "{}" : "{}"'.format(key,
                                                               str(value)[:80]))
                elif isinstance(api_response['result'], list):
                    for value in api_response['result']:
                        print('        --> "{}"'.format(str(value)[:80]))
                else:
                    print('        --> "{}"'.format(str(api_response['result']
                                                        )[:80])) 
        
    def _proxy(self):
        if self.ssl:
            self.path = 'https://{}{}'.format(self.ssl, self.path)
        self.url = urllib.parse.urlparse(self.path)
        # this proxy only works for the grooveshark api endpoint
        if (self.url.netloc.endswith('grooveshark.com') and
            self.url.path.startswith('/more.php')):
            self._grooveshark()
        else:
            self.send_error(500)
    
    def _connect(self):
        # sniff the ssl connection using fake certificates
        self.send_response(200)
        self.end_headers()
        try:
            connection = ssl.wrap_socket(self.connection,
                                         keyfile=server.ssl_key,
                                         certfile=server.ssl_cert,
                                         server_side=True)
            Proxy(connection, self.client_address, self.server,
                  self.headers['Host'])
        except ssl.SSLError:
            pass
    
    # disable logging
    def _dummy(self, *args, **kwargs):
        pass
    
    log_request = _dummy
    log_error = _dummy
    log_message = _dummy
    
    # proxy get and post directly - fake certificates on connect
    do_GET = _proxy
    do_POST = _proxy
    do_CONNECT = _connect

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('local analyzer proxy only '
                                                  'for /more.php'))
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=12345, type=int)
    parser.add_argument('--ssl_key', help='ssl key for man in the middle',
                        default=os.path.join(__path__, 'analyzer',
                                             'grooveshark.key'))
    parser.add_argument('--ssl_cert',
                        help='ssl certificate for man in the middle',
                        default=os.path.join(__path__, 'analyzer',
                                             'grooveshark.crt'))
    parser.add_argument('--methods', default=False, action='store_true',
                        help='create a list of available methods')
    
    arguments = parser.parse_args()
    
    print('--> starting proxy')
    print('--> listening on {}:{}'.format(arguments.host, arguments.port))
    print('--> ssl key: {}'.format(arguments.ssl_key))
    print('--> ssl certificate: {}'.format(arguments.ssl_cert))
    
    server = ThreadingHTTPServer((arguments.host, arguments.port), Proxy)
    server.ssl_key = arguments.ssl_key
    server.ssl_cert = arguments.ssl_cert
    server.lock = threading.Lock()
    server.methods = [] if arguments.methods else None
    server.sessions = {}
    server.serve_forever()