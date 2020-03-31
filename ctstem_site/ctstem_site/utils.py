# utils.py
import datetime
import os

def get_filename(filename):
  now = datetime.datetime.now()
  dt = now.strftime("%Y-%m-%d-%H-%M-%S-%f")
  filename_base, filename_ext = os.path.splitext(filename)
  return '%s_%s%s' % (filename_base.lower(), dt, filename_ext.lower(),)
