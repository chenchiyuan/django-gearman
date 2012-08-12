# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

import uuid
import json

class BaseTask(object):
  def map(self):
    pass

  def callback(self, worker, job):
    json_data = json.loads(job.data)
    return json.dumps(self.on_callback(json_data))

  def on_callback(self, json_data):
    pass

  def sync_run(self, need_unique=False):
    json_datas = self.map()

    for json_data in json_datas:
      if need_unique:
        json_data['unique'] = str(uuid.uuid1())
      self.on_callback(json_data)

  def on_success(self):
    pass

  def reduce(self):
    pass
