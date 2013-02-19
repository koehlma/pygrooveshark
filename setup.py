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

import grooveshark

setup(name=grooveshark.__short_name__,
      version=grooveshark.__version__,
      description=grooveshark.__desc_short__,
      long_description=grooveshark.__desc_long__,
      author=grooveshark.__author__,
      author_email=grooveshark.__email__,
      url=grooveshark.__website__,
      download_url=grooveshark.__download_url__,
      license='GPLv3+',
      packages=['grooveshark', 'grooveshark.classes'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: MacOS :: MacOS X', # Should work on MacOS X I think...
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Multimedia :: Sound/Audio'])