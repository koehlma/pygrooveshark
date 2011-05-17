#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tempfile
import subprocess

import grooveshark

client = grooveshark.Client()
client.init()
null = open('/dev/null', 'wb')
radio = client.radio(grooveshark.RADIO_METAL)
for i in range(0, 1000):
    song = radio.song
    print '%i: %s - %s - %s' % (i + 1, song.name, song.artist.name, song.album.name)
    stream = song.stream
    output = tempfile.NamedTemporaryFile(suffix='.mp3', prefix='grooveshark_')
    process = None
    try:
        output.write(stream.data.read(524288))
        process = subprocess.Popen(['/usr/bin/mplayer', output.name], stdout=null, stderr=null)
        data = stream.data.read(2048)
        while data:
            output.write(data)
            data = stream.data.read(2048)
        process.wait()
    except KeyboardInterrupt:
        if process:
            process.kill()
    output.close()
null.close()