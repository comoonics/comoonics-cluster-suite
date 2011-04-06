def get_defaultsfiles():
    import os.path
    default_dir = "/etc/comoonics"
    home_dir = os.path.join(os.environ['HOME'], ".comoonics")
    globalcfgdefault_file= os.path.join(default_dir, "tools.cfg") 
    localcfgdefault_file= os.path.join(home_dir, "tools.cfg")
    return globalcfgdefault_file, localcfgdefault_file

def get_defaultsenvkey():
    return "COMOONICS_TOOLS_CFG" 

#############
# $Log: __init__.py,v $
# Revision 1.1  2011-02-15 14:58:21  marc
# initial revision
#
