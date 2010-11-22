import unittest
# Implicitly try to import DBLogger and let it register
#try:
#    from comoonics.db.ComDBLogger import DBLogger
#except:
#    pass
class testComLog(unittest.TestCase):

    def __testLogger(self, name, logger):
        try:
            from comoonics import ComLog
            logger.debug("debug")
            logger.info("info")
            logger.warning("warning")
            logger.error("error")
            logger.critical("critical")
            try:
                raise IOError("testioerror")
            except IOError:
#        debugTraceLog(name)
#        infoTraceLog(name)
#        warningTraceLog(name)
                ComLog.errorTraceLog(name)
#        criticalTraceLog(name)
        except:
            self.assert_("Unexpected exception caught!")
    
    def testlogger(self):
        import logging
        import inspect
        import os.path
        from comoonics import ComLog
        _mylogger=logging.getLogger("comoonics.ComLog")
        logging.basicConfig()
        _mylogger.setLevel(logging.DEBUG)
        #from comoonics.db.ComDBLogger import DBLogger
        #registerHandler("DBLogger", DBLogger)
        _filenames=("loggingconfig.ini", "loggingconfig.xml")
        ComLog.getLogger().info("Testing ComLog:")
        loggers={"test1": logging.DEBUG,
                 "test2": logging.INFO,
                 "test3": logging.WARNING}
        for loggername in loggers.keys():
            print "%s level: %s" %(loggername, logging.getLevelName(loggers[loggername]))
            ComLog.setLevel(loggers[loggername], loggername)
            self.__testLogger(loggername, ComLog.getLogger(loggername))

        print("mylogger without level")
        self.__testLogger("mylogger", ComLog.getLogger("mylogger"))
        cp=None

        print("ComLog._classregistry: %s" %ComLog._classregistry)
        for _filename in _filenames:
            logging.shutdown()
            print("Testing configfile %s" %_filename)
            ComLog.fileConfig(os.path.join(os.path.dirname(inspect.getfile(self.__class__)), _filename), None, )
            rootlogger=ComLog.getLogger()
            self.__testLogger("root", rootlogger)
            print("handlernames: %s" %rootlogger.manager.loggerDict.keys())
            for _lname in [ "atix", "atix", "atix.atix1" ]:
                self.__testLogger(_lname, logging.getLogger(_lname))
                self.__testLogger(_lname+".test", logging.getLogger(_lname+".test"))

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(testComLog)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
