'''
Created on Feb 26, 2010

@author: marc
'''
import unittest

from comoonics.storage.ComArchive import TarArchiveHandler, TarBz2ArchiveHandler,  TarGzArchiveHandler, ArchiveHandlerFactory 
# Testing starts here
class myTarArchiveHandler(TarArchiveHandler):
    FORMAT="testformat"
    TYPE="testtype"
class myTarBz2ArchiveHandler(TarBz2ArchiveHandler):
    FORMAT="testformat"
    TYPE="testtype"
class myTarGzArchiveHandler(TarGzArchiveHandler):
    FORMAT="testformat"
    TYPE="testtype"

class Test1(unittest.TestCase):
    def __TestRegisterArchiveHandler(self, theclass):
        ArchiveHandlerFactory.registerArchiveHandler(theclass)

    def __TestRetreiveArchiveHandler(self, theclass):
        ArchiveHandlerFactory.getArchiveHandler("testname", theclass.FORMAT, theclass.TYPE, theclass.COMPRESSION)

    def testRegisterArchiveHandler(self):
        try:
            self.__TestRegisterArchiveHandler(myTarArchiveHandler)
            self.__TestRegisterArchiveHandler(myTarGzArchiveHandler)
            self.__TestRegisterArchiveHandler(myTarBz2ArchiveHandler)
        except:
            self.fail("testRegisterArchiveHandler has failed")

    def testRetreiveArchiveHandler(self):
        try:
            self.__TestRetreiveArchiveHandler(myTarArchiveHandler)
            self.__TestRetreiveArchiveHandler(myTarGzArchiveHandler)
            self.__TestRetreiveArchiveHandler(myTarBz2ArchiveHandler)
        except:
            self.fail("testRegisterArchiveHandler has failed")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()