#!/usr/bin/python
"""
Class for expressing time periods and formating them as regular expression with special given format
i.e. */1-10/* 16:*:* is a format expressing all months from 1-10 and there the hour 16.
Then
TimeExpression.format("*/1-10/* 16:*:*", format)
format can be any format derived from TimeFormat
"""

from comoonics import ComLog
from comoonics.AutoDelegator import AutoDelegator
from comoonics.search.SearchFormat import RESearchFormat

def split(string, sep, values=None, default="*"):
    _string=string.strip()
    _values=_string.count(sep)
    if _string != "":
        _values=_values+1
        _retlist=_string.split(sep)
    else:
        _retlist=list()
    if values and _values < values:
        _retlist.extend([default]*(values-_values))
    return _retlist
    
class TimeExpression(object):
    logger=ComLog.getLogger("TimeExpression")
    months_map={"Jan.*":1, "Feb.*":2, "Mar.*":3, "Apr.*":4, "May":5, "Jun.*":6, "Jul.*":7, "Aug.*":8, "Sep.*":9, "Oct.*":10, "Nov.*":11, "Dec.*":12}
    months=("Jan\w*", "Feb\w*", "Mar\w*", "Apr\w*", "Mai", "Jun\w*", "Jul\w*", "Aug\w*", "Sep\w*", "Oct\w*", "Nov\w*", "Dec\w*")
    def __init__(self, time_expression):
        super(TimeExpression, self).__init__()
        #self.timezone=".*"
        #time_expression=TimeExpression.toRegExp(time_expression)
        if time_expression=="now":
            import time
            time_expression=time.strftime("%Y/%m/%d %H:%M:*")
        (date, time)=split(time_expression, " ", 2)
        (self.year, self.month, self.day)=split(date, "/", 3)
        (self.hour, self.minute, self.second)=split(time, ":", 3)
    def __str__(self):
        return "%s/%s/%s %s:%s:%s" %(self.year, self.month, self.day, self.hour, self.minute, self.second)
    def format(self, _format):
        time_format=TimeFormat(_format)
        TimeExpression.logger.debug("time_format: %s" %(time_format))
        return time_format.format(self)
    def now():
        return TimeExpression("now")
    def toRegExp(string, format="[A-Za-z0-9]"):
        regexps=( ("(\d{1,4})-(\d{1,4})", "[\g<1>-\g<2>]"),
                  ("(\B|[^\.])\*", "\g<1>%s" %(format)),
                  ("(\B|[^\.])\+","\g<1>%s" %(format) ))
        import re
        for (regexp,subs) in regexps:
            string=re.sub(regexp, subs, string)
        return string

    def toHourRegExp(string):
        return "(?P<hour>"+TimeExpression.toRegExp(string,"\d{1,2}")+")"
    def toMinuteRegExp(string):
        return "(?P<minute>"+TimeExpression.toRegExp(string,"\d{1,2}")+")"
    def toSecondRegExp(string):
        return "(?P<second>"+TimeExpression.toRegExp(string,"\d{1,2}")+")"
    def toYearRegExp(string):
        return "(?P<year>"+TimeExpression.toRegExp(string,"\d{2,4}")+")"
    def toMonthnumberRegExp(string):
        string=TimeExpression.toRegExp(string, "1-12")
        import re
        regexp=re.compile("%s" %("|".join(TimeExpression.months)))
        return "(?P<month>["+regexp.sub(TimeExpression.toMonthnumber, string)+"])"
    def toMonthnameRegExp(string):
        
        #ComLog.getLogger().debug("toMonthnameRegExp(%s)" %(str))
        import re
        # resolve the [\d+-\d+] expressions to name1|name2|name3..
        regexp=re.compile("(\d{1,2})-(\d{1,2})")
        _match=regexp.match(string)
        if _match:
            low=int(_match.group(1))
            if low > 0:
                low=low-1
            high=int(_match.group(2))
#            print "%s, %s" %(_match.group(1), _match.group(2))
            string="|".join(TimeExpression.months[low:high])
        elif re.match("^\.\*", string) or re.match("^\*", string):
            string="|".join(TimeExpression.months)
        regexp=re.compile("\d{1,2}")
        return "(?P<month>"+regexp.sub(TimeExpression.toMonthname, string)+")"
    def toMonthDayRegExp(string):
        return "(?P<day>"+TimeExpression.toRegExp(string,"\d{1,2}")+")"

    def toMonthname(number, isregexp=True):
        if isregexp:
            _number=int(number.group(0))
        else:
            _number=int(number)
        #print "%u=>%s" %(_number, TimeExpression.months[_number-1])
        return TimeExpression.months[_number-1]

    def toMonthnumber(name, isregexp=True):
        import re
        if isregexp:
            _name=name.group(0)
        else:
            _name=name
        for key in TimeExpression.months_map.keys():
            if re.match(key, _name):
                #print "%s=>%u" %(_name, int(TimeExpression.months_map[key]))
                return str(TimeExpression.months_map[key])
        return None

    now=staticmethod(now)
    toRegExp=staticmethod(toRegExp)
    toMonthname=staticmethod(toMonthname)
    toMonthnumber=staticmethod(toMonthnumber)
    toYearRegExp=staticmethod(toYearRegExp)
    toMonthnameRegExp=staticmethod(toMonthnameRegExp)
    toMonthnumberRegExp=staticmethod(toMonthnumberRegExp)
    toMonthDayRegExp=staticmethod(toMonthDayRegExp)
    toHourRegExp=staticmethod(toHourRegExp)
    toMinuteRegExp=staticmethod(toMinuteRegExp)
    toSecondRegExp=staticmethod(toSecondRegExp)

class TimeFormat(RESearchFormat):
    """ Base Class for Time Formats"""
    __logStrLevel__ = "TimeFormat"

#    def __new__(cls, *args, **kwds):
#        return object.__new__(DateFormat, args, kwds)
    def __init__(self, _searchfor=None, _formatstring=None):
        super(TimeFormat, self).__init__(_searchfor, _formatstring)
    def format(self, time_expression=None):
        return super(TimeFormat, self).format(time_expression)

class DateFormat(TimeFormat):
    logger=ComLog.getLogger("comoonics.search.datatime.DateFormat")
    format_string=""
    _formated=False
    def __init__(self, _searchfor=None, _formatstring="%d/%b/%Y:%h:%M:%S"):
        super(DateFormat, self).__init__(_searchfor, _formatstring)

    #def clear(self):
    #    super(DateFormat, self).clear()
    #    self._formated=False

    def format(self, time_expression=None):
        #DateFormat.logger.debug("format: formated: %s" %self._formated)
        if not self._formated:
            if not time_expression:
                time_expression=TimeExpression(self.searchfor)
            if isinstance(time_expression, basestring):
                time_expression=TimeExpression(time_expression)
            DateFormat.logger.debug("format: time_expression: %s" %time_expression)
            regexps=list()
            if self.format_string.find("%Y")>=0:
                regexps.append(("%Y", "%s" %(TimeExpression.toYearRegExp(time_expression.year))))
            if self.format_string.find("%m")>=0:
                regexps.append(("%m", "%s" %(TimeExpression.toMonthnumberRegExp(time_expression.month))))
            if self.format_string.find("%d")>=0:
                regexps.append(("%d", "%s" %(TimeExpression.toMonthDayRegExp(time_expression.day))))
            if self.format_string.find("%h")>=0:
                regexps.append(("%h", "%s" %(TimeExpression.toHourRegExp(time_expression.hour))))
            if self.format_string.find("%M")>=0:
                regexps.append(("%M", "%s" %(TimeExpression.toMinuteRegExp(time_expression.minute))))
            if self.format_string.find("%S")>=0:
                regexps.append(("%S", "%s" %(TimeExpression.toSecondRegExp(time_expression.second))))
            if self.format_string.find("%b")>=0:
                regexps.append(("%b", "%s" %(TimeExpression.toMonthnameRegExp(time_expression.month))))
            import re
            _format=self.format_string
            for (regexp,subs) in regexps:
                _format=re.sub(regexp, subs, _format)
            self._format=_format
            self._formated=True
        return self._format

    def getYear(self, default=""):
        return self._getMatchValue("year", default)

    def getMonth(self, default=""):
        return self._getMatchValue("month", default)

    def getDay(self, default=""):
        return self._getMatchValue("day", default)

    def getHour(self, default=""):
        return self._getMatchValue("hour", default)

    def getMinute(self, default=""):
        return self._getMatchValue("minute", default)

    def getSecond(self, default=""):
        return self._getMatchValue("second", default)

    def timeHash(self):
        #if self.getMatch():
        #    DateFormat.logger.debug("%s/%s/%s:%s:%s:%s, match: %s" %(int(self.getYear("0")),\
        #                                                             TimeExpression.toMonthnumber(self.getMonth("Jan"), False), int(self.getDay("0")),\
        #                                                             int(self.getHour("0")),int(self.getMinute("0")), int(self.getSecond("0")), self.getMatch()))
        return "%04u%02u%02u%02u%02u%02u" %(int(self.getYear("0")),\
            int(TimeExpression.toMonthnumber(self.getMonth("Jan"), False)), int(self.getDay("0")),\
            int(self.getHour("0")),int(self.getMinute("0")), int(self.getSecond("0")))

    def _getMatchValue(self, _key, _default=""):
        _value=_default
        if self.getMatch():
            try:
                _value=self.getMatch().group(_key)
            except IndexError:
                pass
        return _value

class SyslogDateFormat(DateFormat):
    format_string="%b\s+%d %h:%M:%S"
    def __init__(self, _searchfor=None, format_string="%b\s+%d %h:%M:%S"):
        super(SyslogDateFormat, self).__init__(_searchfor, format_string)

class ApacheCombinedLogDateFormat(DateFormat):
    format_string="%d/%b/%Y:%h:%M:%S"
    def __init__(self, _searchfor=None, format_string="%d/%b/%Y:%h:%M:%S"):
        super(ApacheCombinedLogDateFormat, self).__init__(_searchfor, format_string)

class ApacheErrorLogDateFormat(DateFormat):
    format_string="%b %d %h:%M:%S %Y"
    def __init__(self, _searchfor=None, format_string="%b %d %h:%M:%S %Y"):
        super(ApacheErrorLogDateFormat, self).__init__(_searchfor, format_string)
class GuessedDateFormat(AutoDelegator):
    logger=ComLog.getLogger("comoonics.search.datatime.GuessedDateFormat")
    _guess_formats=list()
    def registerFormat(_format):
        GuessedDateFormat._guess_formats.append(_format)
    registerFormat=staticmethod(registerFormat)
    def getFormats():
        return GuessedDateFormat._guess_formats
    getFormats=staticmethod(getFormats)

    def __init__(self, _searchfor=None, format_string=None):
        super(GuessedDateFormat, self).__init__()
        self._stub=None
        GuessedDateFormat.logger.debug("__init__: searchfor: %s" %_searchfor)
        self.searchfor=_searchfor
        self.format_string=format_string
    def found(self, _line, _searchfor=None, _flags=0):
        if not _searchfor:
            _searchfor=self.searchfor
        if len(self.delegates)==0:
            GuessedDateFormat.logger.debug("found: init formats")
            _formats=GuessedDateFormat.getFormats()
            for _format in _formats:
                _found=_format.found(_line, "*/*/* *:*:*", _flags)
                #_format._found=False
                _format._formated=False
                if _found:
                    GuessedDateFormat.logger.debug("found: adding delegate: %s" %_format.__class__.__name__)
                    self.delegates.append(_format)
                    self.searchfor=_format.createRESearchFor(_searchfor)
                    GuessedDateFormat.logger.debug("found: cashing searchfor: %s=>%s" %(_searchfor, self.searchfor))
                    break
        if len(self.delegates)>0:
            method=super(GuessedDateFormat, self).__getattr__("found", False, False)
            #GuessedDateFormat.logger.debug("found: will searchfor: %s" %_searchfor)
            found=method(_line, _searchfor, _flags)
            #GuessedDateFormat.logger.debug("found: searchfor: %s, delegates: %s, found: %s" %(_searchfor, self.delegates, found))
            return found
        else:
            return False
    def format(self, _format=None):
        if len(self.delegates)==0:
            return None
        else:
            super(GuessedDateFormat, self).format(_format)
GuessedDateFormat.registerFormat(SyslogDateFormat())
GuessedDateFormat.registerFormat(ApacheCombinedLogDateFormat())
GuessedDateFormat.registerFormat(ApacheErrorLogDateFormat())

###################
# $Log: TimeExpression.py,v $
# Revision 1.2  2009-07-01 11:33:49  marc
# - moved to unittests
# - bugfixes with locking
# - bugfixes with wrong format
#
# Revision 1.1  2007/09/25 11:52:07  marc
# initial revision
#
# Revision 1.1  2007/01/04 10:05:37  marc
# initial revision
#