'''
Created on 06.08.2013

@author: marc
'''
import unittest

class Test(unittest.TestCase):
   backupproperties={
                     "cmd": "./sm_cmd",
                     "client": "testclient",
                     "group": "testgroup",
                     "level": "D"}
   jobname="job123"
   groupname="group123"
   taskname="task123"
   def testSesamBackupHandler1(self):
      import comoonics.backup.SepSesam
      self.assertRaises(comoonics.backup.SepSesam.SepSesam.SepSesamIsNotInstalledError, 
                        comoonics.backup.SepSesam.SepSesamBackupHandler.SepSesamBackupHandler, self.taskname, {"job":self.jobname})
      
   def testSesamBackupHandler2(self):
      import comoonics.backup.SepSesam
      self.assertRaises(TypeError, 
                        comoonics.backup.SepSesam.SepSesamBackupHandler.SepSesamBackupHandler, self.taskname)
      
   def testSesamBackupHandler3(self):
      import comoonics.backup.SepSesam
      self.assertTrue(comoonics.backup.SepSesam.SepSesamBackupHandler.SepSesamBackupHandler(self.taskname, self.backupproperties))
      
   def testSesamBackupGroupCreate(self):
      if self.backupproperties.has_key("job"): del self.backupproperties["job"] 
      self.backupproperties.update({"group": self.groupname, "taskname": self.taskname})
      self.assertMultiLineEqual(self._testSesamAction(self.taskname, self.backupproperties, 
                                                      "createArchive", "/tmp", None, True), 
                                """add task %(taskname)s -G %(group)s -c %(client)s -s /tmp
backup %(taskname)s -G %(group)s -l %(level)s
remove task %(taskname)s
""" %self.backupproperties)
   
   def testSesamBackupGroup(self):
      if self.backupproperties.has_key("job"): del self.backupproperties["job"] 
      self.backupproperties.update({"group": self.groupname})
      self.assertMultiLineEqual(self._testSesamAction("", self.backupproperties, 
                                                      "createArchive", "/tmp", None, False), 
                                """backup -G %(group)s -l %(level)s
""" %self.backupproperties)
   
   def testSesamBackupJobCreate(self):
      if self.backupproperties.has_key("group"): del self.backupproperties["group"]
      self.backupproperties.update({"job": self.jobname, "taskname": self.taskname})
      self.assertMultiLineEqual(self._testSesamAction(self.taskname, self.backupproperties, 
                                                      "createArchive", "/tmp", None, True), 
                                """add task %(taskname)s -j %(job)s -c %(client)s -s /tmp
backup %(taskname)s -j %(job)s -l %(level)s
remove task %(taskname)s
""" %self.backupproperties)
      
   def testSesamBackupJob(self):
      if self.backupproperties.has_key("group"): del self.backupproperties["group"]
      self.backupproperties.update({"job": self.jobname})
      self.assertMultiLineEqual(self._testSesamAction("", self.backupproperties, 
                                                      "createArchive", "/tmp", None, False), 
                                """backup -j %(job)s -l %(level)s
""" %self.backupproperties)
   
   def _testSesamAction(self, jobname, properties, action, *args):
      import comoonics.backup.SepSesam
      handler=comoonics.backup.SepSesam.SepSesamBackupHandler.SepSesamBackupHandler(jobname, properties)
      return getattr(handler, action)(*args)

if __name__ == "__main__":
   #import sys;sys.argv = ['', 'Test.testName']
   unittest.main()