#!/usr/bin/env python
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

from __future__ import print_function

import sys

import gobject

import grooveshark

try:
    import gplayer
except ImportError:
    print('GPlayer module is missing.')
    print('Please load it from https://github.com/koehlma/snippets/tree/master/gplayer...')
    sys.exit()

class Player(object):
    def __init__(self):
        self._client = grooveshark.Client()
        self._client.init()
        self._popular = list(self._client.popular())
        self._player = gplayer.Player()
        self._player.connect('finished', self._finished)
        self._current = 0
    
    def _finished(self, player):
        self._current += 1
        self._play()
    
    def _play(self):
        self._check_current()
        print('%s - %s - %s' % (self._popular[self._current].name, self._popular[self._current].artist.name,
                                self._popular[self._current].album.name))
        self._stream = self._popular[self._current].stream
        self._player.play_cache(gplayer.Cache(self._stream.data, self._stream.size))
    
    def _check_current(self):
        if self._current < 0:
            self._current = len(self._popular) - 1
        elif self._current > len(self._popular) - 1:
            self._current = 0    
    
    def start(self):
        self._play()
    
    def stop(self):
        self._player.stop()

if __name__ == '__main__':
    player = Player()
    player.start()
    try:
        gplayer.main()
    except KeyboardInterrupt:
        player.stop()