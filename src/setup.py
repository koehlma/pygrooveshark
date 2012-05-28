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

from distutils.core import setup

from grooveshark import __version__

setup(name='pygrooveshark',
      version=__version__,
      author='Maximilian Köhl',
      author_email='linuxmaxi@googlemail.com',
      url='http://www.github.com/koehlma/pygrooveshark',
      license='GPLv3',
      packages=['grooveshark', 'grooveshark.classes'])
