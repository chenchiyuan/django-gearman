# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from django.views.decorators.csrf import csrf_exempt
from tasks import BaseTask
from django.http import HttpResponse

@csrf_exempt
def task_dispatch(request, name):
  def get_handle(name):
    handle_list = BaseTask.__subclasses__()
    handle = None

    for sub in handle_list:
      if name.lower() == sub.__name__.lower():
        handle = sub
        break
    return handle

  handle = get_handle(name)
  if not handle:
    return HttpResponse("No handle")

  handle().reduce(**request.POST)
  return HttpResponse(name)