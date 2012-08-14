# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

from redis import StrictRedis
from django.conf import settings

class RedisCache(StrictRedis):
  pass

cache = RedisCache(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

