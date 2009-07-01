import unittest

class test_TimeExpression(unittest.TestCase):
    split_tests={ "": ["*", "*", "*"], 
                  "*": ["*", "*", "*"],
                  "*/*": ["*", "*", "*"],
                  "*/*/*": ["*", "*", "*"],
                  "1": ["1", "*", "*"],
                  "1/1": ["1", "1", "*"],
                  "1/1/1": ["1", "1", "1"]}
    formater_teststrs= [ "*/1-10/* 16:*:*", "*/9/* 04:*:*", "now", "2009/06/25 *:*:*", "*" ]
    def test_toMonthnumberRegExp(self):
        from comoonics.search.datetime.TimeExpression import TimeExpression
        results={ "Jan-Oct": "(?P<month>[1-10])",
                 "*": "(?P<month>[1-12])" }
        for input, result1 in results.items():
            result2=TimeExpression.toMonthnumberRegExp(input)
            error= "toMonthnumberRegExp(%s) => %s == %s" %(input, result2, result1)
            print error
            self.assertTrue(result2==result1, error)
    
    def test_toMonthnameRegExp(self):
        from comoonics.search.datetime.TimeExpression import TimeExpression
        results={ "1-10": "(?P<month>Jan\w*|Feb\w*|Mar\w*|Apr\w*|Mai|Jun\w*|Jul\w*|Aug\w*|Sep\w*|Oct\w*)",
                  "*": "(?P<month>Jan\w*|Feb\w*|Mar\w*|Apr\w*|Mai|Jun\w*|Jul\w*|Aug\w*|Sep\w*|Oct\w*|Nov\w*|Dec\w*)" }
        for input, result1 in results.items():
            result2=TimeExpression.toMonthnameRegExp(input)
            error= "toMonthnameRegExp(%s) => %s == %s" %(input, result2, result1)
            print error
        
    def test_toMonthname(self):
        result="Sep\w*"
        from comoonics.search.datetime.TimeExpression import TimeExpression
        monthnum=9
        monthname=TimeExpression.toMonthname(monthnum, False)
        print "Mtimeonth %u: %s" %(monthnum, monthname)
        self.assertEquals(monthname, result, "Monthnum %u is not %s as expected. %s" %(monthnum, monthname, result))
    
    def test_toMonthNumber(self):
        result="11"
        from comoonics.search.datetime.TimeExpression import TimeExpression
        monthname="Nov"
        monthnum=TimeExpression.toMonthnumber(monthname, False)
        print "Month %s: %s" %(monthname, monthnum)
        self.assertEquals(monthnum, result, "Month %s is not %s as expected. %s" %(monthname, monthnum, result))

    def test_split(self):
        from comoonics.search.datetime.TimeExpression import split
        for _input, _result1 in self.split_tests.items(): 
            _result2=split(_input, "/", 3, "*")
            _error="split(%s, /, 3, *) => %s == %s)" %(_input, _result2, _result1)
            print _error
            self.assertEquals(_result1, _result2, "split(%s, /, 3, *)=> %s != %s" %(_input, _result2, _error))

    def basetest_TimeExpression_toRegExp(self, teststr, _resultstr1):
        from comoonics.search.datetime.TimeExpression import TimeExpression
        _resultstr2=TimeExpression.toRegExp(teststr)
        _error="Testing TimeExpression.toRegExp(%s): %s == %s" %(teststr, _resultstr2, _resultstr1)
        print _error
        self.assertEquals(_resultstr1, _resultstr2, _error)


    def basetest_Formater_format(self, formaterinstance, teststr, _resultstr1):
        from comoonics.search.datetime.TimeExpression import TimeExpression
        te=TimeExpression(teststr)
        _resultstr2=formaterinstance.format(te)
        _error="Testing time dateformater.format(%s): %s == %s " %(teststr, _resultstr2, _resultstr1)
        print _error
        self.assertEquals(_resultstr1, _resultstr2, _error)

    def test_toRegExp(self):
        results=["[A-Za-z0-9]/[1-10]/[A-Za-z0-9] 16:[A-Za-z0-9]:[A-Za-z0-9]",
                 "[A-Za-z0-9]/9/[A-Za-z0-9] 04:[A-Za-z0-9]:[A-Za-z0-9]",
                 "now",
                 "2009/06/25 [A-Za-z0-9]:[A-Za-z0-9]:[A-Za-z0-9]",
                 "[A-Za-z0-9]"]
        for i in range(len(self.formater_teststrs)):
            self.basetest_TimeExpression_toRegExp(self.formater_teststrs[i], results[i])

    def now(self):
        import time
        _now=time.localtime()
        now=list()
        now.append("%u" %_now[0])
        now.append("%02u" %_now[1])
        now.append("%02u" %_now[2])
        now.append("%02u" %_now[3])
        now.append("%02u" %_now[4])
        return now

    def test_SyslogDateFormat_format(self):
        from comoonics.search.datetime.TimeExpression import SyslogDateFormat, TimeExpression
        now=self.now()
        results=["(?P<month>Jan\w*|Feb\w*|Mar\w*|Apr\w*|Mai|Jun\w*|Jul\w*|Aug\w*|Sep\w*|Oct\w*)\s+(?P<day>\d{1,2}) (?P<hour>16):(?P<minute>\d{1,2}):(?P<second>\d{1,2})",
                 "(?P<month>Sep\w*)\s+(?P<day>\d{1,2}) (?P<hour>04):(?P<minute>\d{1,2}):(?P<second>\d{1,2})",
                 "(?P<month>%s)\s+(?P<day>%s) (?P<hour>%s):(?P<minute>%s):(?P<second>\d{1,2})" %(TimeExpression.toMonthname(now[1], False), now[2], now[3], now[4]),
                 "(?P<month>Jun\w*)\s+(?P<day>25) (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})",
                 "(?P<month>Jan\w*|Feb\w*|Mar\w*|Apr\w*|Mai|Jun\w*|Jul\w*|Aug\w*|Sep\w*|Oct\w*|Nov\w*|Dec\w*)\s+(?P<day>\d{1,2}) (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})"]
        for i in range(len(self.formater_teststrs)):
            self.basetest_Formater_format(SyslogDateFormat(), self.formater_teststrs[i], results[i])
            
    def test_ApacheCombindeLogDateFormat(self):
        from comoonics.search.datetime.TimeExpression import ApacheCombinedLogDateFormat, TimeExpression
        now=self.now()
        results=["(?P<day>\d{1,2})/(?P<month>Jan\w*|Feb\w*|Mar\w*|Apr\w*|Mai|Jun\w*|Jul\w*|Aug\w*|Sep\w*|Oct\w*)/(?P<year>\d{2,4}):(?P<hour>16):(?P<minute>\d{1,2}):(?P<second>\d{1,2})",
                 "(?P<day>\d{1,2})/(?P<month>Sep\w*)/(?P<year>\d{2,4}):(?P<hour>04):(?P<minute>\d{1,2}):(?P<second>\d{1,2})",
                 "(?P<day>%s)/(?P<month>%s)/(?P<year>%s):(?P<hour>%s):(?P<minute>%s):(?P<second>\d{1,2})" %(now[2], TimeExpression.toMonthname(now[1], False), now[0], now[3], now[4]),
                 "(?P<day>25)/(?P<month>Jun\w*)/(?P<year>2009):(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})",
                 "(?P<day>\d{1,2})/(?P<month>Jan\w*|Feb\w*|Mar\w*|Apr\w*|Mai|Jun\w*|Jul\w*|Aug\w*|Sep\w*|Oct\w*|Nov\w*|Dec\w*)/(?P<year>\d{2,4}):(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})"]
        for i in range(len(self.formater_teststrs)):
            self.basetest_Formater_format(ApacheCombinedLogDateFormat(), self.formater_teststrs[i], results[i])
            
    def test_ApacheErrorLogDateFormat(self):
        from comoonics.search.datetime.TimeExpression import ApacheErrorLogDateFormat, TimeExpression
        now=self.now()
        results=["(?P<month>Jan\w*|Feb\w*|Mar\w*|Apr\w*|Mai|Jun\w*|Jul\w*|Aug\w*|Sep\w*|Oct\w*) (?P<day>\d{1,2}) (?P<hour>16):(?P<minute>\d{1,2}):(?P<second>\d{1,2}) (?P<year>\d{2,4})",
                 "(?P<month>Sep\w*) (?P<day>\d{1,2}) (?P<hour>04):(?P<minute>\d{1,2}):(?P<second>\d{1,2}) (?P<year>\d{2,4})",
                 "(?P<month>%s) (?P<day>%s) (?P<hour>%s):(?P<minute>%s):(?P<second>\d{1,2}) (?P<year>%s)" %(TimeExpression.toMonthname(now[1], False), now[2], now[3], now[4], now[0]),
                 "(?P<month>Jun\w*) (?P<day>25) (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2}) (?P<year>2009)",
                 "(?P<month>Jan\w*|Feb\w*|Mar\w*|Apr\w*|Mai|Jun\w*|Jul\w*|Aug\w*|Sep\w*|Oct\w*|Nov\w*|Dec\w*) (?P<day>\d{1,2}) (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2}) (?P<year>\d{2,4})"]
        for i in range(len(self.formater_teststrs)):
            self.basetest_Formater_format(ApacheErrorLogDateFormat(), self.formater_teststrs[i], results[i])
            
    def test_SyslogMessages(self):
        messages={ "Jun 25 09:35:27 node qdiskd[9951]: <warning> qdisk cycle took more than 3 seconds to complete (4.880000)": True,
                   "Jun 24 19:11:22 node qdiskd[9951]: <warning> qdisk cycle took more than 3 seconds to complete (3.130000)": True }
        from comoonics.search.datetime.TimeExpression import SyslogDateFormat
        formater=SyslogDateFormat("*")
        for message, matches1 in messages.items():
            matches2=formater.found(message)
            print message
            _error= "format: %s; %s == %s" %(formater, matches1, matches2)
            print _error
            self.assertTrue(matches1==matches2, _error)
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
