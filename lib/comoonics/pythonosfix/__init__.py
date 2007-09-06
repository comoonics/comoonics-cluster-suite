"""Comoonics os_fix

Module to bypass os-path-realpath bug in python python-2.3.4-14.4
Does not attach fix if another python version is used.
"""

import sys

_names = sys.builtin_module_names
if 'posix' in _names and sys.version == "2.3.4 (#1, Jan  9 2007, 16:40:09) \n[GCC 3.4.6 20060404 (Red Hat 3.4.6-3)]":
    from comoonics import ComLog
    log = ComLog.getLogger("comoonics.os_fix")
    log.info("Using os_fix to retrieve a working version of os.path.realpath with python 2.3 .")
    
    from os import *    
    import realpath as path
else:
    from os import *