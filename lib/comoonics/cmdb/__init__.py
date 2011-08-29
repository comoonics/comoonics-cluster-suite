"""

Init this package

"""
def get_defaultsfiles():
    import os.path
    default_dir = "/etc/comoonics"
    home_dir = os.path.join(os.environ.get('HOME', ''), ".comoonics")
    globalcfgdefault_file= os.path.join(default_dir, "cmdb.cfg") 
    localcfgdefault_file= os.path.join(home_dir, "cmdb.cfg")
    return globalcfgdefault_file, localcfgdefault_file

def get_defaultsenvkey():
    return "COMOONICS_CMDB_CFG" 

########
# $Log: __init__.py,v $
# Revision 1.1  2007-03-05 16:10:30  marc
# first rpm version
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#