def get_defaultsfiles():
    import os.path
    default_dir = "/etc/comoonics"
    home_dir = os.path.join(os.environ['HOME'], ".comoonics")
    globalcfgdefault_file= os.path.join(default_dir, "cluster-tools.cfg") 
    localcfgdefault_file= os.path.join(home_dir, "cluster-tools.cfg")
    return globalcfgdefault_file, localcfgdefault_file

def get_defaultsenvkey():
    return "COMOONICS_CLUSTER_TOOLS_CFG" 
