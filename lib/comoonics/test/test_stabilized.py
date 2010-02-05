"""
Testcases for stabilized
"""
from comoonics import stabilized
import unittest
import logging

if __name__ == '__main__':

    stabilized.logger.setLevel(logging.DEBUG)
    class testStabilized(unittest.TestCase):
        files=[ "/proc/scsi/scsi"]
        hash_results=[ True, True ]
        mtime_results=[ False, True ]
        def testHash(self):
            self.__test__("mtime", self.files, self.mtime_results)
            self.__test__("hash", self.files, self.hash_results)
        def __test__(self, _type, _files, _results):
            for i in range(len(_files)):
                _file=_files[i]
                _res=_results[i]
                print "Testing stabilized.stabilized<%s> on file: %s" %(_type, _file)
                self.assertEqual(stabilized.stabilized(type=_type, file=_file, interval=120.0, iterations=11), _res)

    unittest.main()