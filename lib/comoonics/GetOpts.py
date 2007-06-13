#!/usr/bin/python
"""Com.oonics GetOpts

Class to make getopts very easy

"""

# here is some internal information
# $Id: GetOpts.py,v 1.5 2007-06-13 09:10:12 marc Exp $
#

__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/GetOpts.py,v $

import getopt
import ComExceptions, ComLog
import logging
import sys

class NoErrorBreak(ComExceptions.ComException): pass

class Option(object):
    def __init__(self, name, description, value, required=False, short_opt=None, func=None):
        """
           Constructor(name, description, value, required=False, short_opt=None, func=None)
        """
        self.name=name
        self.description=description
        self.value=value
        self.required=required
        self.short_opt=short_opt
        if func:
            self.func=func
        else:
            self.func=self.do
    def do(self, newvalue):
        self.value=newvalue
    def __str__(self):
        return self.value

class PrivateOption(Option):
    """Option not being listed in usage """
    def __init__(self, name, value, required=False, short_opt=None, func=None):
        Option.__init__(name, "", value, required, short_opt, func)

class HelpOption(Option):
    def __init__(self, parent):
        Option.__init__(self, "help", "this help", False, False, "h", parent.help)

class VersionOption(Option):
    def __init__(self, version):
        Option.__init__(self, "version", "output the version", False, False, "v", self.do)
        self.version=version

    def do(self, newvalue):
        Option.do(self, newvalue)
        print "Version: %s" %self.version
        raise NoErrorBreak("")

class BaseConfig(object):
    def __init__(self, cmdname, description, version, options=None):
        self.__cmdname__=cmdname
        import sys
        self.__stdout__=sys.stdout
        self.__stderr__=sys.stderr
        self.__version__=version
        self.__description__=description
        self.__ljust__=10
        self.__value__="value"
        self.__gap__=5
        if options:
            for option in options:
                self.__dict__[option.name]=option

        if not self.__dict__.has_key("help"):
            self.help=HelpOption(self)
        if not self.__dict__.has_key("version"):
            self.version=VersionOption(self.__version__)
        self.genShortOpts()
        self.additional_param_str=""

    def genShortOpts(self):
        pass

    def getAdditionalParams(self):
        return self.additional_param_str

    def setAdditionalParams(self, params):
        self.additional_param_str=params

    def usage(self):
        print >>self.__stdout__, "%s %s %s" %(self.__cmdname__,self.getAllOptionString(),self.getAdditionalParams())
        if self.__dict__.has_key("__description__"):
            print >>self.__stdout__, "\t%s" %(self.__description__)
        for option in self.__dict__.values():
            if not isinstance(option, Option):
                continue
            if isinstance(option, PrivateOption):
                continue
            print >>self.__stdout__, "\t%s" %(self.getOptionString(option))

    def help(self, rest):
        self.usage()
        raise NoErrorBreak("")

    def getAllOptionString(self):
        buf=""
        for option in self.__dict__.values():
            if not isinstance(option, Option):
                continue
            if option.short_opt and option.required and type(option.value) == bool:
                buf=buf+" -%s|--%s" %(option.short_opt, option.name)
            elif option.short_opt and not option.required and type(option.value) == bool:
                buf=buf+" [-%s|--%s]" %(option.short_opt, option.name)
            elif option.short_opt and option.required and type(option.value) != bool:
                buf=buf+" -%s|--%s value" %(option.short_opt, option.name)
            elif option.short_opt and not option.required and type(option.value) != bool:
                buf=buf+" [-%s|--%s value]" %(option.short_opt, option.name)
            elif not option.short_opt and option.required and type(option.value) == bool:
                buf=buf+" --%s" %(option.name)
            elif not option.short_opt and not option.required and type(option.value) == bool:
                buf=buf+" [--%s]" %(option.name)
            elif not option.short_opt and option.required and type(option.value) != bool:
                buf=buf+" --%s value" %(option.name)
            elif not option.short_opt and not option.required and type(option.value) != bool:
                buf=buf+" [--%s value]" %(option.name)

        return buf

    def getOptionString(self, option):
        buf=""
        if option.short_opt and type(option.value) == bool:
            buf=" -%s|--%s" %(option.short_opt, option.name)
        elif option.short_opt and type(option.value) != bool:
            buf=" -%s|--%s %s" %(option.short_opt, option.name, self.__value__)
        elif not option.short_opt and type(option.value) == bool:
            buf=" --%s" %(option.name)
        elif not option.short_opt and type(option.value) != bool:
            buf=" --%s %s" %(option.name, self.__value__)
        buf=buf.ljust(self.__ljust__)
        if type(option.value) == bool:
            buf=buf+"%s" %(option.description)
        else:
            buf=buf+"%s (default: %s)" %(option.description, option.value)

        return buf

    def getoptShort(self):
        buf=""
        for option in self.__dict__.values():
            if not isinstance(option, Option):
                continue
            if option.short_opt and type(option.value) == bool:
                buf=buf+"%s" %(option.short_opt)
            elif option.short_opt:
                buf=buf+"%s:" %(option.short_opt)
        return buf

    def getoptLong(self):
        long_opts=list()
        __add__=0
        for option in self.__dict__.values():
            if not isinstance(option, Option):
                continue
            if self.__ljust__ < len(option.name)+5:
                self.__ljust__=len(option.name)+5+self.__gap__
            if type(option.value)!=bool and __add__==0:
                __add__=len(self.__value__)+1
            if type(option.value) == bool:
                long_opts.append(option.name)
            else:
                long_opts.append("%s=" %(option.name))
        self.__ljust__=self.__ljust__+__add__
        return long_opts

    def getShortOption(self, opt):
        for option in self.__dict__.values():
            if not isinstance(option, Option):
                continue
            if option.short_opt and option.short_opt == opt:
                return option

        raise getopt.GetoptError("Unknown parameter %s" % opt)

    def getopt(self, args):
        try:
            (__opts__, __args_proper__)=getopt.getopt(args, self.getoptShort(), self.getoptLong())
            for (opt, value) in __opts__:
                if not value:
                    value=True
                opt=opt.lstrip("-")
#                ComLog.getLogger().info("Option %s, %s" % (opt, value))
                if len(opt)==1:
                    option=self.getShortOption(opt)
                elif self.__dict__.has_key(opt):
                    option=self.__dict__[opt]
                else:
                    option=self.__dict__[opt.replace("-", "_")]
                ret=option.func(value)
                if ret > 0:
                    return ret

            return self.do(__args_proper__)
        except NoErrorBreak, noe:
            return -1
        except getopt.GetoptError, goe:
            print >>self.__stderr__, "Error parsing params: %s" % goe
            self.usage()
            return 1

    def __getattribute__(self, name):
        attr=object.__getattribute__(self, name)
        if isinstance(attr, Option):
            return attr.value
        else:
            return attr

    def do(self, args_proper):
        pass

    def setDebug(self, value):
        ComLog.setLevel(logging.DEBUG)

class TestConfig(BaseConfig):
    def __init__(self):
        import sys
        BaseConfig.__init__(self, sys.argv[0], "Test config for Getopts comoonics.", __version__)
        self.debug=Option("debug", "toggle debugmode", False, False, "d", self.setDebug)
        self.opt1=Option("opt1", "First Option", "5", False, "o")
        self.opt2=Option("opt2", "Second Option", "123", False)
        self.opt3=Option("opt3", "Third Option", "abc", False, "q")

    def do(self, args_proper):
        if len(args_proper) > 0:
            print >>self.__stderr__, "Wrong syntax."
            self.usage(sys.argv)
            return 1

def main():
    config=TestConfig()
    print "Testing help short"
    config.getopt(["-h"])
    print "Testing help long"
    config.getopt(["--help"])
    print "Testing version long"
    config.getopt(["--version"])
    print "Testing debug short and opt1 long xy"
    config.getopt(["-d", "--opt1=xy"])

if __name__ == '__main__':
    main()


##################
# $Log: GetOpts.py,v $
# Revision 1.5  2007-06-13 09:10:12  marc
# - fixed error newer occured (include sys)
#
# Revision 1.4  2007/02/22 15:25:22  marc
# access to Option attributes returns now the value
#
# Revision 1.3  2006/12/13 20:16:52  marc
# - added PrivatOption
# - added AllOptionString
#
# Revision 1.2  2006/09/28 08:45:42  marc
# bugfix for options without values
#
# Revision 1.1  2006/09/19 10:36:59  marc
# initial revision
#