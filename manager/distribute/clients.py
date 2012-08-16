# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from gearman.client import GearmanClient
from manager.utils import get_gearman_host

import logging

logger = logging.getLogger(__name__)

class Client(GearmanClient):
  def __init__(self, host_list=get_gearman_host(), *args, **kwargs):
    super(Client, self).__init__(host_list, *args, **kwargs)

  def send_job(self, name, data, unique=False, *args, **kwargs):
    logger.info("Send job task %s, %r" %(name, data))
    self.submit_job(task=name, data=data, unique=unique, *args, **kwargs)

  def send_jobs(self, jobs, wait_until_complete=False, background=False):
    logger.info("Send jobs task num %d" %(len(jobs)))
    return self.submit_multiple_jobs(jobs, wait_until_complete=wait_until_complete,
                                     background=background)
