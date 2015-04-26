#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Copyright (C) 2015, Maximilian Köhl <mail@koehlma.de>
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
Grooveshark Analyzer
--------------------

Grooveshark Analyzer is a debug and reverse engineer proxy for the unofficial
Grooveshark API. To use it you have to route all traffic to `grooveshark.com`
through it. It will then show you some useful information about API calls.
"""

import argparse
import datetime
import http.server
import json
import os.path
import pprint
import re
import ssl
import socketserver
import threading
import urllib.parse

import requests


__version__ = '2.0'
__path__ = os.path.dirname(__file__)


class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self, connection, client_address, server, host=None):
        self.host = host
        super().__init__(connection, client_address, server)

    def _proxy(self):
        if self.host:
            self.path = 'https://' + self.host + self.path
        url = urllib.parse.urlparse(self.path)
        self.server.analyzer.analyze(url, self)

    def _connect(self):
        self.send_response(200)
        self.end_headers()
        try:
            connection = ssl.wrap_socket(self.connection,
                                         keyfile=self.server.ssl_key,
                                         certfile=self.server.ssl_cert,
                                         server_side=True)
            Handler(connection, self.client_address,
                    self.server, self.headers['Host'])
        except ssl.SSLError:
            pass

    def _dummy(self, *args, **kwargs):
        pass

    log_request = _dummy
    log_error = _dummy
    log_message = _dummy

    do_GET = _proxy
    do_POST = _proxy
    do_CONNECT = _connect


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, analyzer, host='127.0.0.1', port=12345,
                 ssl_key=None, ssl_cert=None):
        self.analyzer = analyzer
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        super().__init__((host, port), Handler)


class Analyzer():
    def __init__(self, output_directory):
        self.sessions = {}
        self.lock = threading.Lock()
        self.output_directory = output_directory

    def _analyze_api(self, url, data, handler, response, session_id):
        request = json.loads(data.decode('utf-8'))
        result = response.json().get('result', None)
        if request['header']['session']:
            session_id = request['header']['session']
        if request['method'] == 'getCommunicationToken' and session_id:
            self.sessions[session_id]['token'] = response['result']
        with self.lock:
            session = self.sessions[session_id]
            client = request['header']['client']
            client_revision = request['header']['clientRevision']
            user_id = request['header']['uuid']
            country = request['header']['country']
            token = request['header']['token']
            print('--> Session "{}":'.format(session_id))
            print('    --> Communication Token:', session['token'])
            print('    --> Method:', request['method'])
            print('    --> Client:', client, client_revision)
            print('    --> UUID:', user_id)
            print('    --> Country:', country)
            print('    --> Token:', token)
            print('    --> Parameters:')
            for key, value in request['parameters'].items():
                print('        --> "{}" : "{}"'.format(key, str(value)[:80]))
            if result:
                print('    --> Result:')
                if isinstance(result, dict):
                    for key, value in result.items():
                        str_value = str(value)[:80]
                        print('        --> "{}" : "{}"'.format(key, str_value))
                elif isinstance(result, list):
                    for value in result:
                        print('        --> "{}"'.format(str(value)[:80]))
                else:
                    print('        --> "{}"'.format(str(result)[:80]))

    def _analyze_preload(self, url, data,  handler, response, session_id):
        match = re.search(r'"getCommunicationToken"\s*:\s*"([0-9a-f]+)"',
                          response.text)
        if match and session_id:
            self.sessions[session_id]['token'] = match.group(1)

    def analyze(self, url, handler):
        if handler.headers['Content-Length']:
            length = int(handler.headers['Content-Length'])
            data = handler.rfile.read(length)
        else:
            data = None

        response = requests.request(handler.command, handler.path, data=data,
                                    headers=handler.headers)

        if self.output_directory:
            now = datetime.datetime.today()
            name = now.strftime('%m_%d_%Y_%H:%m:%S_%s_%f')

            request_filename = os.path.join(self.output_directory, name +
                                            '.request')
            with open(request_filename, 'wb') as request_file:
                request_file.write(handler.requestline.encode('ascii'))
                request_file.write(str(handler.headers).encode('ascii'))
                if data:
                    request_file.write(data)

            response_filename = os.path.join(self.output_directory, name +
                                             '.response')
            with open(response_filename, 'wb') as response_file:
                response_file.write(str(response.status_code).encode('ascii'))
                response_file.write((' ' + response.reason).encode('ascii'))
                for key, value in response.headers.items():
                    response_file.write(b'\r\n')
                    response_file.write(key.encode('ascii'))
                    response_file.write(b': ')
                    response_file.write(value.encode('ascii'))
                response_file.write(b'\r\n\r\n')
                try:
                    content = pprint.pformat(response.json())
                    response_file.write(content.encode('utf-8'))
                except ValueError:
                    response_file.write(response.content)

        handler.send_response(response.status_code)
        for key, value in response.headers.items():
            if key == 'transfer-encoding':
                continue
            elif key == 'content-length':
                continue
            elif key == 'content-encoding':
                continue
            handler.send_header(key, value)
        handler.send_header('Content-Length', len(response.content))
        handler.end_headers()
        handler.wfile.write(response.content)

        session_id = response.cookies.get('PHPSESSID', None)
        if session_id and session_id not in self.sessions:
            self.sessions[session_id] = {'token': None}

        if url.path.startswith('/more.php'):
            self._analyze_api(url, data, handler, response, session_id)
        elif url.path.startswith('/preload.php'):
            self._analyze_preload(url, data, handler, response, session_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=12345, type=int)
    parser.add_argument('--ssl', nargs=2, metavar=('KEY', 'CERT'))
    parser.add_argument('-o', '--output-directory')

    args = parser.parse_args()

    if args.ssl:
        ssl_key = args.ssl[0]
        ssl_cert = args.ssl[1]
    else:
        ssl_key = os.path.join(__path__, 'ssl', 'gs.key')
        ssl_cert = os.path.join(__path__, 'ssl', 'gs.crt')

    analyzer = Analyzer(args.output_directory)

    server = Server(analyzer, args.host, args.port, ssl_key, ssl_cert)
    server.serve_forever()


if __name__ == '__main__':
    main()