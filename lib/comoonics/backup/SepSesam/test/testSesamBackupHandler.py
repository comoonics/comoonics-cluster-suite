'''
Created on 06.08.2013

@author: marc
'''
import unittest

class Test(unittest.TestCase):
   def testSesamBackupHandler(self):
      import comoonics.backup.SepSesam
      self.assertRaises(comoonics.backup.SepSesam.SepSesam.SepSesamIsNotInstalledError, comoonics.backup.SepSesam.SepSesamBackupHandler.SepSesamBackupHandler, "handler123")

if __name__ == "__main__":
   #import sys;sys.argv = ['', 'Test.testName']
   unittest.main()