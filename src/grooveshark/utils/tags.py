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

import json
import urllib.request

TAG_URL = 'http://grooveshark.com/gs/models/tags_with_ids.json'
TRANSLATE_URL = 'http://static.a.gs-cdn.net/locales/gs-en.json'


def tags():
    tags = json.loads(urllib.request.urlopen(TAG_URL).read().decode('utf-8'))
    translation = json.loads(
        urllib.request.urlopen(TRANSLATE_URL)
        .read().decode('utf-8')[len('localeCallback_en('):-len(');')])
    return tags, translation

if __name__ == '__main__':
    tags, translation = tags()
    print('Tags:')
    for tag, number in tags.items():
        print('    GENRE_{} = {}'.format(tag.upper(), number))
    print('\n')
    print('Documentation:')
    print('    +-------------------------------------+-------------------------------+')
    print('    | Constant                            | Genre                         |')
    print('    +=====================================+===============================+')
    for tag in tags:
        if 'STATION_' + tag.upper() in translation:
            print('    | {:<36}| {:<32}|'.format(
                ':const:`Radio.GENRE_' + tag.upper() + '`',
                translation['STATION_' + tag.upper()].replace('&amp;', ' and ')))
            print('    +-------------------------------------+-------------------------------+')
