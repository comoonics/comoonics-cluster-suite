import unittest

class test_ComException(unittest.TestCase):    

    def testComException(self):
        from comoonics.ComExceptions import ComException
        try:
            raise ComException, "Error: testmessage"
        except ComException, ce:
            pass
        except Exception, e:
            self.assert_("Wrong exception caught. %s" %e)

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(test_ComException)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
