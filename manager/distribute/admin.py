# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from gearman.admin_client import GearmanAdminClient
from manager.distribute.workers import Worker
from manager.utils import get_gearman_host

import json
import os

class Admin(GearmanAdminClient):
  def __init__(self, host_list=get_gearman_host(), *args, **kwargs):
    super(Admin, self).__init__(host_list=host_list, *args, **kwargs)
    self.host_list = host_list

  def get_status(self):
    return super(Admin, self).get_status()

  def get_workers(self):
    return super(Admin, self).get_workers()

  def get_version(self):
    return super(Admin, self).get_version()

  def get_response_time(self):
    return super(Admin, self).ping_server()

  def empty_task(self, task):
    def callback(worker, job):
      return json.dumps({'a': 'a'})

    worker = Worker(self.host_list)
    worker.register_task(task, callback)
    worker.safely_work()

  def start_server(self, port=4730):
    os.system('gearmand -d -L 0.0.0.0 -p %s' %str(port))
    print("Job Server Start at port %s" %str(port))

  def send_shutdown(self, graceful=True):
    print("Job Server will shutdown")
    return super(Admin, self).send_shutdown(graceful)