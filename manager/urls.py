# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.conf.urls import patterns, include, url
from manager.tasks import BaseTask
from views import task_dispatch

#
#def url_pattern():
#  subclasses = BaseTask.__subclasses__()
#  def pattern(name):
#    style = '^%s/$' %name
#    return url(style, name='callback_%s' %name, view=name)
#
#  ls = []
#  for sub in subclasses:
#    ls.append(pattern(sub.__name__.lower()))
#
#  return patterns('', *ls)
#
#urlpatterns = url_pattern()

urlpatterns = patterns('',
  url('^%s/$' %(r'(?P<name>[\-_0-9a-zA-Z\.]+)'), view=task_dispatch, name='dispatch'),
)