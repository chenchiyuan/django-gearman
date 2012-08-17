# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function, with_statement
from BeautifulSoup import BeautifulSoup
from ribida import API

def parse_content(dom, file_name, **kwargs):
  with open(file_name, 'r') as f:
    soup = BeautifulSoup(f.read())

    divs = soup.findAll(dom, **kwargs)
    if not divs:
      return {}

    api = API()
    tags_all = api.parse_words(title='', content=divs[0].text,
                               imagine=False, TF_IDF=False)
    show = tags_all.get('show', {})
    hide = tags_all.get('hide', {})
    show.update(hide)
    return show