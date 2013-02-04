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

__version__ = '4.0'
__project__ = 'Python Grooveshark'
__short_name__ = 'pygrooveshark'
__author__ = 'Maximilian Köhl'
__email__ = 'linuxmaxi@googlemail.com'
__website__ = 'http://www.github.com/koehlma/pygrooveshark'
__download_url__ = 'https://github.com/koehlma/pygrooveshark/tarball/master'
__source__ = 'https://github.com/koehlma/pygrooveshark/'
__vcs__ = 'git://github.com/koehlma/pygrooveshark.git'
__copyright__ = 'Copyright (C) 2012, Maximilian Köhl'
__desc_short__ = 'An unofficial Grooveshark API for Python.'
__desc_long__ = ('This is an unofficial Grooveshark API for Python. It supports'
                 'the popular songs list as well as searching for songs, albums,'
                 'artists and listening to radio stations. This also works in'
                 'Germany where Grooveshark officially is not available. It'
                 'supports Python 2 as well as Python 3.')

__all__ = ['JSQueue', 'HTMLShark', 'Album', 'Artist', 'Picture', 'Playlist',
           'Station', 'Song', 'Stream', 'API', 'Session']

from grooveshark.backends import PySide, Requests, Urllib
from grooveshark.clients import JSQueue, HTMLShark
from grooveshark.objects import (Album, Artist, Picture, Playlist, Station,
                                 Song, Stream)
from grooveshark.api import Connection, Client