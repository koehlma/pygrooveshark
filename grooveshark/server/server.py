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
import threading
import time
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
from grooveshark.classes import *

STATE_READING = 0
STATE_FINISHED = 1
STATE_CANCELED = 2

class Cache(object):
    '''
    Reads out the whole file object to avoid for example stream timeouts.
    Use :class:`Player`'s :meth:`play_cache` method to play this object.
    
    Attention: This starts a new thread for reading.
    If you want to cancel this thread you have to call the :meth:`cancel` method.
    If you call :class:`Player`'s :meth:`stop` method the :meth:`cancel` method is automatically called.
    
    :param fileobj: file object to cache
    :param size: size to calculate state of caching (and playing)
    :param seekable: file object is seekable (not implemented yet)
    :param blocksize: size of blocks for reading and caching
    '''
    def __init__(self, fileobj, size, blocksize=2048):
        self._fileobj = fileobj
        self.size = size
        self._blocksize = blocksize
        self.state = STATE_READING
        self._memory = []
        self._current = 0
        self._active = True
        self.bytes_read = 0
        self._read_thread = threading.Thread(target=self._read)
        self._read_thread.start()
        
    def _read(self):
        data = self._fileobj.read(self._blocksize)
        while data and self._active:
            self._memory.append(data)
            self.bytes_read += len(data)
            data = self._fileobj.read(self._blocksize)
        if self._active:
            self.state = STATE_FINISHED
        self._fileobj.close()
    
    def reset(self):
        self._current = 0
        
    @property
    def offset(self):
        return self._current
    
    @offset.setter
    def offset(self, offset):
        self._current = offset
    
    def cancel(self):
        '''
        Cancels the reading thread.
        '''
        if self.state == STATE_READING:
            self._active = False
            self.state = STATE_CANCELED
        
    def read(self, size=None):
        '''
        Reads in the internal cache.
        This method should not be used directly.
        The :class:`Player` class uses this method to read data for playing.
        '''
        start_block, start_bytes = divmod(self._current, self._blocksize)
        if size:
            if size > self.size - self._current:
                size = self.size - self._current
            while self._current + size > self.bytes_read:
                time.sleep(0.01)
            self._current += size
            end_block, end_bytes = divmod(self._current, self._blocksize)
            result = self._memory[start_block:end_block]
        else:
            while self.size > self.bytes_read:
                time.sleep(0.01)
            self._current = self.size
            result = self._memory[start_block:]
        if size:
            if end_bytes > 0 :
                result.append(self._memory[end_block][:end_bytes])
        if start_bytes > 0 and result:
            result[0] = result[0][start_bytes:]
        return b''.join(result)              
        
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
        if os.path.isdir(document):
            document += '/index.html'
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
    
    def _command_stream(self, query):
        song = Song.from_export(json.loads(query['song'][0]), self.server.client.connection)
        if song.id in self.server.streams:
            stream, cache = self.server.streams[song.id]
        else:
            self.log_message('GS Stream Request')
            stream = song.stream
            cache = Cache(stream.data, stream.size)
            self.server.streams[song.id] = stream, cache
        if 'Range' in self.headers:
            self.send_response(206)
            start_byte, end_byte = self.headers['Range'].replace('bytes=', '').split('-')
            if start_byte:
                start_byte = int(start_byte)
            else:
                start_byte = 0
            if end_byte:
                end_byte = int(end_byte)
            else:
                end_byte = stream.size
            cache.offset = start_byte
            self.send_response(206)
            if 'download' in query:
                self.send_header('Content-Disposition', 'attachment; filename="%s - %s - %s.mp3"' % (song.name, song.album.name, song.artist.name))
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Type', stream.data.info()['Content-Type'])
            self.send_header('Content-Length', stream.data.info()['Content-Length'])
            self.send_header('Content-Range', 'bytes %i-%i/%i' % (start_byte, end_byte, stream.size))
            self.end_headers()
            sended_bytes = 0
            while sended_bytes < end_byte:
                if end_byte - sended_bytes < 2048:
                    data = cache.read(end_byte - sended_bytes)
                else:
                    data = cache.read(2048)
                sended_bytes += len(data)
                self.wfile.write(data)                  
        else:
            cache.reset()
            self.send_response(200)
            if 'download' in query:
                self.send_header('Content-Disposition', 'attachment; filename="%s - %s - %s.mp3"' % (song.name, song.album.name, song.artist.name))
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Type', stream.data.info()['Content-Type'])
            self.send_header('Content-Length', stream.data.info()['Content-Length'])
            self.end_headers()
            data = cache.read(2048)
            while data:
                self.wfile.write(data)
                data = cache.read(2048)
            
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
    print(client.init())
    server = ThreadingHTTPServer(address, Server)
    server.www = os.path.join(os.path.dirname(__file__), 'www')
    server.streams = {}
    server.client = client
    server.serve_forever()

if __name__ == '__main__':
    main()