# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

from manager.utils import get_gearman_host
from gearman.worker import GearmanWorker
import json
import threading

import logging

logger = logging.getLogger(__name__)

WILL_SHUT_DOWN = 2
SHUT_DOWN = 1

class Worker(GearmanWorker):
  def __init__(self, host_list=get_gearman_host()):
    self.continue_work = 10
    super(Worker, self).__init__(host_list=host_list)

  def on_job_execute(self, current_job):
    return super(Worker, self).on_job_execute(current_job)

  def on_job_exception(self, current_job, exc_info):
    return super(Worker, self).on_job_exception(current_job, exc_info)

  def on_job_complete(self, current_job, job_result):
    print("Current_job %r complete" %current_job)
    json_data = json.loads(job_result)
    if isinstance(json_data, dict) and json_data.has_key('SHUTDOWN'):
      self.continue_work = WILL_SHUT_DOWN
      return super(Worker, self).on_job_complete(current_job, job_result)
    return super(Worker, self).on_job_complete(current_job, job_result)

  def safely_work(self):
    self.continue_work = 10
    try:
      self.work()
    except Exception, err:
      logger.error(err)
      pass

  def after_poll(self, any_activity):
    return True

  def poll_connections_until_stopped(self, submitted_connections, callback_fxn, timeout=None):
    def smart_callback(any_activity):
      if self.continue_work == WILL_SHUT_DOWN:
        self.continue_work -= 1
        return callback_fxn(any_activity)
      elif self.continue_work == SHUT_DOWN:
        self.continue_work -= 1
        return callback_fxn(any_activity) and self.continue_work
      else:
        return callback_fxn(any_activity) and self.continue_work

    super(Worker, self).poll_connections_until_stopped(submitted_connections,
                                                       smart_callback, timeout=timeout)


class ThreadWorker(threading.Thread):
  def __init__(self, task, callback, daemon=False, host_list=get_gearman_host()):
    threading.Thread.__init__(self)
    self.task = task
    self.callback = callback
    self.daemon = daemon
    self.worker = Worker(host_list=host_list)

  def run(self):
    self.worker.register_task(self.task, self.callback)
    self.worker.safely_work()
