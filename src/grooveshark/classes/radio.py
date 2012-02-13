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

class Radio(object):
    '''
    Listen to songs by specifc genre.
    Do not use this class directly.
    
    :param artists: list of artist ids
    :param radio: the genre (see :class:`Client`'s :meth:`radio` method)
    :param connection: the underlying :class:`Connection` object
    '''
    def __init__(self, artists, radio, connection, recent_artists=[], songs_already_seen=[]):
        self._artists = [artist['ArtistID'] for artist in artists]
        self._radio = radio
        self._connection = connection
        self._recent_artists = list(recent_artists)
        self._songs_already_seen = list(songs_already_seen)
    
    @classmethod
    def from_export(cls, export, connection):
        return cls(export['artists'], export['radio'], connection, export['recent_artists'], export['songs_already_seen'])
    
    @property
    def song(self):
        '''
        :class:`Song` object of next song to play
        '''
        song = self._connection.request('autoplayGetSong', {'weightModifierRange' : [-9,9],
                                                            'seedArtists' : dict([(artist, 'p') for artist in self._artists]),
                                                            'tagID' : self._radio, 'recentArtists' : self._recent_artists, 
                                                            'songQueueID' : self._connection.queue_id, 'secondaryArtistWeightModifier' : 0.75,
                                                            'country' : self._connection.country, 'seedArtistWeightRange' : [110,130],
                                                            'songIDsAlreadySeen' : self._songs_already_seen, 'maxDuration' : 1500,
                                                            'minDuration' : 60, 'frowns' : []},
                                        self._connection.header('autoplayGetSong', 'jsqueue'))[1]
        return Song(song['SongID'], song['SongName'], song['ArtistID'], song['ArtistName'], song['AlbumID'], song['AlbumName'],
                    song['CoverArtUrl'], None, song['EstimateDuration'], None, self._connection)
    
    def export(self):
        '''
        Returns a dictionary with all song information.
        Use the :meth:`from_export` method to recreate the
        :class:`Song` object.
        '''
        return {'artists' : self._artists, 'radio' : self._radio, 'recent_artists' : self._recent_artists, 'songs_already_seen' : self._songs_already_seen}
    
from grooveshark.classes.song import Song