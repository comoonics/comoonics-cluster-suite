'''
Created on Nov 17, 2010

@author: marc
'''
import unittest
from comoonics.tools.XMLConfigParser import ConfigParser
from comoonics import ComLog

class Test(unittest.TestCase):

    def line(self, text):
        print "--------------------- %s -------------------" %text

    def setUp(self):
        import inspect
        import os.path
        self.filename=os.path.join(os.path.dirname(inspect.getfile(self.__class__)), "loggingconfig.xml")
        self.cp=ConfigParser()
        self.cp.read(self.filename)
        self.loggers=["atix", "atix.atix1", "atix.atix2"]
        ComLog.fileConfig(self.filename)
        
    def testSections(self):
        sections=self.cp._sections.keys()
        sections.sort()
        expectedsections=[u'formatter_form01', u'formatter_form02', u'formatter_form03', u'formatter_form04', 'formatters', u'handler_atix', u'handler_atix1', u'handler_atix2', u'handler_root', 'handlers', u'logger_atix', u'logger_atix1', u'logger_root', 'loggers']
        self.assertEquals(sections, expectedsections, "Expected sections are different from sections %s!=%s" %(sections, expectedsections))

    def testKeys(self):
        expectedsections={ ConfigParser.LOGGERS_TAGNAME: "atix1,root,atix", ConfigParser.HANDLERS_TAGNAME: "atix1,atix2,root,atix", ConfigParser.FORMATTERS_TAGNAME: "form02,form01,form04,form03"}
        for section in (ConfigParser.LOGGERS_TAGNAME, ConfigParser.HANDLERS_TAGNAME, ConfigParser.FORMATTERS_TAGNAME):
            _keys=self.cp.get(section, "keys")
            expectedkeys=expectedsections[section]
            self.assertEquals(_keys,expectedkeys, "Keys and expected keys for section %s are different %s!= %s" %(section, _keys, expectedkeys))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()