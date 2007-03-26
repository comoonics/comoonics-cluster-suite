"""

Init this package

"""

from exceptions import ImportError

try:
    import comoonics.backup
except ImportError:
#    print "Importerror of comoonics.backup"
            pass

########
# $Log: __init__.py,v $
# Revision 1.2  2007-03-26 08:15:21  marc
# automatically importing comoonics.backup if available
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#