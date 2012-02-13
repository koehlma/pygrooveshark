# -*- coding: utf-8 -*-

import sys, os

doc_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(doc_directory, '..', 'src'))

import grooveshark.core.client
import grooveshark.classes

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.intersphinx', 'sphinx.ext.todo']

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'Grooveshark-Python'
copyright = u'2011, koehlma'

version = '2.0'
release = '2.0'

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'default'

html_static_path = ['_static']

htmlhelp_basename = 'Grooveshark-Pythondoc'

latex_documents = [
  ('index', 'Grooveshark-Python.tex', u'Grooveshark-Python Documentation',
   u'koehlma', 'manual'),
]

man_pages = [
    ('index', 'grooveshark-python', u'Grooveshark-Python Documentation',
     [u'koehlma'], 1)
]


intersphinx_mapping = {'http://docs.python.org/': None}
