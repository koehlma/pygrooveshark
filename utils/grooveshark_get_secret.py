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

"""
Because Grooveshark encrypts the security tokens it is not enough anymore to
decompile the Flash application - we need to extract a decrypted version out of
a memory dump. Therefore we search in the whole dump for strings that look like
tokens. After that the potential tokens are validated - we calculate a request
token based on sniffed constants (request method and communication token) and
compare the result with the sniffed request token. If they match we have found
the correct security token.
""" 

__version__ = '1.0'

import argparse
import hashlib
import os
import re

token_format = re.compile(b'[a-z]+([A-Z][a-z]+)+')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('extract secret out of flash'
                                                  'memory dumps'))
    parser.add_argument('method', help='request method')
    parser.add_argument('token', help='communication token')
    parser.add_argument('result', help='request token')
    
    arguments = parser.parse_args()
    
    method = arguments.method
    token = arguments.token
    result_random = arguments.result[:6]
    result_hash = arguments.result[6:]
    
    found = False
    
    dumps = os.listdir(os.getcwd())
    
    print('--> searching')
    for number, dump in enumerate(dumps):
        print('\r--> {}/{}'.format(number, len(dumps)), end='')
        with open(dump, 'rb') as dump:
            for match in token_format.finditer(dump.read()):
                secret = match.group(0).decode('utf-8')
                if hashlib.sha1((method + ':' + token + ':' + secret + ':'+
                                 result_random).encode('utf-8')
                                ).hexdigest() == result_hash:
                    print('\n--> found: {}'.format(secret))
                    found = True
                    break
        if found:
            break