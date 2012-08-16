# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.conf import settings

import uuid
import json
import requests

class BaseTask(object):
  """Base Task
    关键函数：1. map 2. on_callback
    """

  @property
  def post_url(self):
    return 'http://' + settings.HOST + ':' + settings.REMOTE_PORT\
           + '/tasks/' + self.__class__.__name__ + '/'

  def map(self):
    """ 将数据分片
    返回数据是将原有数据分片后的list
    注意分片的数量，太大可能会出问题(send_jobs不是生成器?)
    """
    pass

  def callback(self, worker, job):
    """
    manager实际调用的函数,有简单的数据类型处理。
    """

    json_data = json.loads(job.data)
    result = json.dumps(self.on_callback(json_data))

    if json_data.has_key('SHUTDOWN'):
      result.update({'SHUTDOWN': True})

    return result

  def on_callback(self, json_data):
    """
    任务的实际处理
    """
    pass

  def sync_run(self, need_unique=False):
    """
    task是可以同步执行的，sync_run就是同步执行任务。
    如果sync_run能执行，但是放在gearman中不执行.
    很有可能是数据传输问题。

    """
    json_datas = self.map()

    for json_data in json_datas:
      if need_unique:
        json_data['unique'] = str(uuid.uuid1())
      self.on_callback(json_data)

  def post(self, **kwargs):
    return requests.post(url=self.post_url, data=kwargs)

  def on_success(self):
    pass

  def reduce(self, **kwargs):
    pass
