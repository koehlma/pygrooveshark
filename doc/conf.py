# -*- coding: utf-8 -*-

import sys, os

doc_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(doc_directory, '..'))

import grooveshark

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.intersphinx', 'sphinx.ext.todo']

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'Grooveshark-Python'
copyright = u'2011, linuxmaxi'

version = '0.0.3'
release = '0.0.3'

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'default'

html_static_path = ['_static']

htmlhelp_basename = 'Grooveshark-Pythondoc'

latex_documents = [
  ('index', 'Grooveshark-Python.tex', u'Grooveshark-Python Documentation',
   u'linuxmaxi', 'manual'),
]

man_pages = [
    ('index', 'grooveshark-python', u'Grooveshark-Python Documentation',
     [u'linuxmaxi'], 1)
]


intersphinx_mapping = {'http://docs.python.org/': None}
