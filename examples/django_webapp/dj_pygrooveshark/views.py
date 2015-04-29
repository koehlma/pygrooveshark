from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest
from wsgiref.util import FileWrapper
import simplejson as json
import time

from services.cache import Cache
from grooveshark import Client
from grooveshark.classes.song import Song


client = Client()
client.init()
_cache = {}
_cache['streams'] = {}


def index(request):

    return render_to_response("index.html")


def popular(request):

    if 'popular' not in _cache:
        _cache['popular'] = (
            time.time(),
            [song.export() for song in client.popular()])
    if time.time() - _cache['popular'][0] > 7200:
        _cache['popular'] = (
            time.time(),
            [song.export() for song in client.popular()])

    return HttpResponse(
        json.dumps({'status': 'success', 'result': _cache['popular'][1]}))


def search(request):

    search_type = request.GET.get('type', [Client.SONGS])
    query = request.GET.get('query')

    if query is None:
        return HttpResponseBadRequest('missing query argument')

    if search_type not in (Client.SONGS, Client.ALBUMS, Client.ARTISTS):
        return HttpResponseBadRequest('unknown type')

    result = [obj.export() for obj in client.search(query, search_type)]
    return HttpResponse(json.dumps({'status': 'success', 'result': result}))


def stream(request):

    song = Song.from_export(json.loads(request.GET['song']), client.connection)

    if song.id in _cache['streams']:
        stream, cache = _cache['streams'][song.id]
    else:
        stream = song.stream
        cache = Cache(stream.data, stream.size)
        _cache['streams'][song.id] = stream, cache

    response = HttpResponse()

    if 'HTTP_RANGE' in request.META:

        response.status = 206
        start_byte, end_byte = request.META['HTTP_RANGE'].replace('bytes=', '').split('-')

        if start_byte:
            start_byte = int(start_byte)
        else:
            start_byte = 0

        if end_byte:
            end_byte = int(end_byte)
        else:
            end_byte = stream.size

        cache.offset = start_byte
        if 'download' in request.GET:
            response['Content-Disposition'] = 'attachment; filename="{} - {} - {}.mp3"'.format(song.name, song.album.name, song.artist.name)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Type'] = stream.data.info()['Content-Type']
        response['Content-Length'] = str(stream.size)
        response['Content-Range'] = 'bytes {}-{}/{}'.format(
            start_byte, end_byte, stream.size)

    else:
        cache.reset()
        if 'download' in request.GET:
            response['Content-Disposition'] = 'attachment; filename="{} - {} - {}.mp3"'.format(song.name, song.album.name, song.artist.name)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Type'] = stream.data.info()['Content-Type']
        response['Content-Length'] = str(stream.size)

    response.content = FileWrapper(cache)
    return response
