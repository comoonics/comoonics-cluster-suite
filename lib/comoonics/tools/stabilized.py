"""
StabilizedFile is a module providing the stabilized command in nash.
Supported are HashStabilizedFile and PollStabilizedFile.
Background is to have a tool checking if a file has not changed in content, by polling or with mtime
for some time.
"""

from comoonics import ComLog

logger=ComLog.getLogger("comoonics.stabilized")

class UnsupportedStabilizedOption(Exception):
   def __str__(self):
      return "the stabilized type %s is not implemented or known." %self.args[0]

def stabilized(**kwds):
   """
   stabilized is a module providing the stabilized command in nash.
   Supported types are hash and mtime.
   Background is to have a tool checking if a file has not changed in content, by polling or with mtime
   for some time.
   """
   if not kwds.has_key("file"):
      raise TypeError, "stabilized"
   _file=kwds["file"]
   _type=kwds.get("type", "mtime")
   _iterations=kwds.get("iterations", -1)
   _interval=kwds.get("interval", 750.0)
   _good=kwds.get("good", 10)
   if _type=="mtime":
      _impl=MtimeStabilized(_iterations, _interval, _good)
   elif _type=="hash":
      _impl=HashStabilized(_iterations, _interval, _good)
   else:
      raise UnsupportedStabilizedOption, _type
   return _impl.do(_file)

class Stabilized(object):
   """
   Baseclass for a stabilized file
   """
   def __init__(self, _iterations=-1, _interval=750.0, _good=10):
      self.iterations=_iterations
      self.interval=_interval
      self.good=_good

   def do(self, _file, _iterations=None, _interval=None, _good=None):
      if not _iterations:
         _iterations=self.iterations
      if not _interval:
         _interval=self.interval
      if not _good:
         _good=self.good
      _count=0
      while (_iterations == -1 or _iterations > 0) and _count<_good:
         if self.has_not_changed(_file):
            _count+=1
         else:
            _count=0
         self.udelayspec(_interval)
         if _iterations != -1:
            _iterations-=1
      logger.debug("do(good: %u, wanted: %u)" %(_count, _good))
      if _count>=_good:
         return True
      else:
         return False

   def has_not_changed(self, _file, _current=None):
      if not hasattr(self, "last"):
         self.last=_current
         return False
      elif self.last==_current:
         self.last=_current
         return True
      else:
         self.last=_current
         return False

   def udelayspec(self, _msecs):
      import time
      _start_time = time.time()
      while (time.time() - _start_time) < float(_msecs)/1000.0:
         pass

class HashStabilized(Stabilized):
   def has_not_changed(self, _file):
      checksum=self.checksum(_file)
      return super(HashStabilized, self).has_not_changed(_file, checksum)
   def checksum(self, _file):
      import zlib
      _filed=open(_file, "r")
      _read=_filed.read(16384)
      _adler32=0
      while _read != "":
         _adler32+=zlib.adler32(_read)
         _read=_filed.read(16384)
      _filed.close()
      logger.debug("checksum: %u" %_adler32)
      return _adler32

class MtimeStabilized(Stabilized):
   def has_not_changed(self, _file):
      import os
      import stat
      _mtime=os.stat(_file)[stat.ST_MTIME]
      logger.debug("has_not_changed.mtime(%s): %u" %(_file, _mtime))
