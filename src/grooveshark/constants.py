# -*- coding:utf-8 -*-
#
# Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals, division

class Constants():
    token_timeout = 1200
    user_agent = ('Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) '
                  'Gecko/20121011 Firefox/16.0.1')
    album_cover = 'http://images.grooveshark.com/static/albums/'
    playlist_cover= 'http://images.grooveshark.com/static/playlists/'
    no_cover = 'http://images.grooveshark.com/static/albums/90_album.png'
    country = {'ID' : 0, 'CC4' : 0, 'CC2' : 0, 'CC3' : 0, 'IPR' : 0, 'DMA' : 0,
               'CC1' : 0}
