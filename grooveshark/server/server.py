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
import os.path
import json
import mimetypes
if sys.version[0] == '3':
    import http.server as httpserver
    import socketserver
    from urllib.parse import urlparse, parse_qs, quote_plus
else:
    import BaseHTTPServer as httpserver
    import SocketServer as socketserver
    from urllib import quote_plus
    from urlparse import urlparse, parse_qs
    
import grooveshark.core.client

class Server(httpserver.BaseHTTPRequestHandler):
    def _respond_json(self, data):
        data = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=UTF-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    
    def _bad_request(self, message):
        data = json.dumps({'status' : 'error', 'result' : message}).encode('utf-8')
        self.send_response(400)
        self.send_header('Content-Type', 'application/json; charset=UTF-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    
    def _www(self):
        document = os.path.join(self.server.www, self.url.path[1:])
        if os.path.isfile(document):
            self.send_response(200)
            self.send_header('Content-Type', mimetypes.guess_type(document))
            self.send_header('Content-Length', str(os.path.getsize(document)))
            self.end_headers()
            with open(document, 'rb') as input_document:
                data = input_document.read(2048)
                while data:
                    self.wfile.write(data)
                    data = input_document.read(2048)
        else:
            data = '<span style="font-size:50px"><b>404 Not Found</b></span>'.encode('utf-8')
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
    
    def _command_popular(self, query):
        self.send_response(200)
        result = [song.export() for song in self.server.client.popular()]
        self._respond_json({'status' : 'success', 'result' : result})
    
    def _command_search(self, query):
        if not 'type' in query:
            query['type'] = [grooveshark.core.client.SEARCH_TYPE_SONGS]
        if 'query' in query:
            if not query['type'][0] in [grooveshark.core.client.SEARCH_TYPE_SONGS,
                                        grooveshark.core.client.SEARCH_TYPE_ALBUMS,
                                        grooveshark.core.client.SEARCH_TYPE_ARTISTS]:
                self._bad_request('unknown type')
            else:
                result = [object.export() for object in self.server.client.search(query['query'][0], query['type'][0])]
                self._respond_json({'status' : 'success', 'result' : result})
        else:
            self._bad_request('missing query argument')
    
    def _command_radio(self, query):
        if 'tag' in query:
            radio = self.server.client.radio(query['tag'][0])
            self._respond_json({'status' : 'success', 'result' : radio.export()})            
        else:
            self._bad_request('missing tag argument')        
    
    def _request(self):
        query = parse_qs(self.url.query)
        if 'command' in query:
            command = query['command'][0]
            if hasattr(self, '_command_%s' % (command)):
                getattr(self, '_command_%s' % (command))(query)
            else:
                self._bad_request('unknown command "%s"' % (command))
        else:
            self._bad_request('please specify a command')
    
    def _handle(self):
        self.url = urlparse(self.path)
        if self.url.path == '/':
            self.url = urlparse(self.path + 'index.html')
        if self.url.path == '/request':
            self._request()
        else:
            self._www()
        
    do_GET = _handle
    do_POST = _handle

class ThreadingHTTPServer(socketserver.ThreadingMixIn, httpserver.HTTPServer): pass

def main(address=('0.0.0.0', 8181)):
    '''
    Starts own grooveshark service.
    '''   
    client = grooveshark.core.client.Client()
    client.init()
    server = ThreadingHTTPServer(address, Server)
    server.www = os.path.join(os.path.dirname(__file__), 'www')
    server.client = client
    server.serve_forever()

if __name__ == '__main__':
    main()