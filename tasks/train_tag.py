# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

from utils.parse_html import parse_content
from manager.tasks import BaseTask
from utils import cache
from utils.const import (TRAIN_RELATION_ALL_PREFIX,
              TRAIN_RELATION_PREFIX, TRAIN_TAG_PREFIX, TRAIN_TOTAL)

import os
import json
import logging

logger = logging.getLogger(__name__)

sorted_list = lambda *args: '_'.join(sorted(args))
threshold = 0.06
BASE_FILE = '/home/toureet/web_data/gearman/mafengwo/'
DATA_DIR = 'tasks/data/'

def cache_key(prefix, items):
  if isinstance(items, basestring):
    return prefix + items
  elif isinstance(items, list) or isinstance(items, tuple):
    return prefix + sorted_list(*items)
  else:
    return prefix

def get_min_max(a, b):
  min, max = (a, b) if a < b else (b, a)
  return min, max

class TrainTagTask(BaseTask):
  def __init__(self, names=None,  burst=None):
    self.names = names
    self.burst = burst

  def map(self):
    names = []
    for root, dirs, files in os.walk(BASE_FILE):
      for file in files:
        names.append(file)

    burst = 2

    iters = [{'names': names[i: i+burst]} if (i+burst) < len(names)
             else {'names': names[i: -1]} for i in range(0, len(names), burst)]

    return iters

  def callback(self, worker, job):
    json_data = json.loads(job.data)
    json_data['unique'] = str(job.unique)

    try:
      result = self.on_callback(json_data)
    except Exception as err:
      logger.error(err)
      result = {'success': 'success'}

    return json.dumps(result)

  def on_callback(self, json_data):
    if json_data.has_key('exception'):
      return json.dumps(json_data)

    names = json_data['names']

    path = lambda file_name: BASE_FILE + file_name

    for name in names:
      try:
        self.train(path(name))
      except Exception, err:
        print(err)
        continue

    return json.dumps({'success' : 'Success'})

  def train(self, name=None):
    if not name:
      return
    
    tags = parse_content(dom='div', file_name=name, **{'class': 'a_con_text cont'})

    print("Training...")
    print(','.join(tags.keys()))
    self._train_rate(tags)
    self._train_total(tags)
    self._train_relations_all(tags)
    self._train_relations(tags)
    print("Done")

  def _train_rate(self, tags):
    for tag in tags:
      key = cache_key(TRAIN_TAG_PREFIX, tag)
      value = int(tags[tag])
      cache.incr(name=key, amount=value)

  def _train_total(self, tags):
    if not tags:
      return

    key = cache_key(TRAIN_TOTAL, items=None)
    if len(tags) == 1:
      value = tags.values()[0]
      cache.incr(name=key, amount=int(value))
      return 

    values = tags.values()
    total = reduce(lambda x, y: x+y, values)
    cache.incr(name=key, amount=int(total))

  def _train_relations_all(self, tags):
    import itertools
    if not len(tags) > 1:
      return

    combiantions = itertools.combinations(tags.keys(), 2)
    for a, b in combiantions:
      min, max = get_min_max(a, b)
      value = float(tags[min]/tags[max])
      key_min = cache_key(TRAIN_RELATION_ALL_PREFIX, min)
      key_max = cache_key(TRAIN_RELATION_ALL_PREFIX, max)
      cache.zincrby(name=key_min, value=max, amount=value)
      cache.zincrby(name=key_max, value=min, amount=value)
      
  def _train_relations(self, tags):
    import itertools
    if not len(tags) > 1:
      return 

    total = reduce(lambda x, y: x+y, tags.values())
    real_tags = {}

    for tag in tags:
      if tags[tag]/total > threshold:
        real_tags.update({tag: tags[tag]})

    if not len(real_tags) > 1:
      return 

    combiantions = itertools.combinations(real_tags.keys(), 2)
    for a, b in combiantions:
      min, max = get_min_max(a, b)
      value = float(real_tags[min]/real_tags[max])
      key_min = cache_key(TRAIN_RELATION_PREFIX, min)
      key_max = cache_key(TRAIN_RELATION_PREFIX, max)
      cache.zincrby(name=key_min, value=max, amount=value)
      cache.zincrby(name=key_max, value=min, amount=value)

  def output(self):
    self._tag_rate()
    self._tag_relations(prefix=TRAIN_RELATION_PREFIX)

  def _tag_rate(self):
    import math

    total = int(cache.get(TRAIN_TOTAL))
    file_path = os.path.join(DATA_DIR, 'tag_rate_train.dic')
    file = open(file_path, 'w')

    keys = cache.keys('%s*' %TRAIN_TAG_PREFIX)
    for key in keys:
      name = key[len(TRAIN_TAG_PREFIX):]
      value = float(cache.get(key))
      log = math.log10(total/value)

      line = '%s\t%.3f\n' %(name.decode('utf-8'), log)
      file.write(line.encode('utf-8'))

    file.close()

  def _tag_relations(self, prefix):
    keys = cache.keys('%s*' %prefix)
    file_path = os.path.join(DATA_DIR, '%s.dic' %prefix.replace(':', '_').lower())

    file = open(file_path, 'w')
    for key in keys:
      items = cache.zrevrangebyscore(name=key, min='-inf', max='+inf', withscores=True)
      name = key[len(prefix):]
      total = 0

      for tag, value in items:
        score = cache.get(name=cache_key(TRAIN_TAG_PREFIX, tag.decode('utf-8')))
        total += value/ float(score)

      objs = []
      for tag, value in items:
        score = cache.get(name=cache_key(TRAIN_TAG_PREFIX, tag.decode('utf-8')))
        percentage = value/float(score)/total
        objs.append('%s__%.4f' %(tag.decode('utf-8'), percentage))

      values = ','.join(objs)
      line = '%s\t%s\n' %(name.decode('utf-8'), values)
      file.write(line.encode('utf-8'))

    file.close()

