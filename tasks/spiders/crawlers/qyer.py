# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import unicode_literals, print_function
import requests
import os

AIM_URL = lambda tid: 'http://bbs.qyer.com/viewthread.php?tid=%d&page=1' % tid
FOLDER = '/home/toureet/crawlers/qyer'

HEADERS = {
  'HTTP_REFERER': 'http://bbs.qyer.com/'
}

def parser(tid):
  url = AIM_URL(tid)
  res = requests.get(url, headers=HEADERS)
  data = res.content
  return data

def validate(data):
  if len(data) > 16384:
    return True
  else:
    return False

def get_folder(tid):
  bucket = int(tid/50000)
  name = '%d_%d' %(bucket, bucket+50000)
  return os.path.join(FOLDER, name)

def get_file_path(tid):
  return os.path.join(get_folder(tid), str(tid))

def save(tid, data):
  folder = get_folder(tid)
  exists = os.path.exists(folder)
  if not exists:
    os.makedirs(folder)

  file_path = get_file_path(tid)
  file = open(file_path, 'w')
  file.write(data)

def do_parser(tid):
  print("现在正在爬取穷游论坛,tid=%d" % tid)
  data = parser(tid)
  valid = validate(data)
  if not valid:
    print("没有数据，退出")
    return

  try:
    save(tid, data)
  except Exception, err:
    print("异常结束")
    print(err)
    return

  print("爬取%d，成功" % tid)

def worker(start, end):
  current = 0
  try:
    tids = xrange(start, end)
    for tid in tids:
      if os.path.exists(get_folder(tid)):
        print("爬取过了tid %d" % tid)
        continue

      do_parser(tid)
      current = tid

  except:
    print(current)
