def get_defaultsfiles():
    import os.path
    default_dir = "/etc/comoonics"
    home_dir = os.path.join(os.environ.get('HOME', ''), ".comoonics")
    globalcfgdefault_file= os.path.join(default_dir, "cluster-tools.cfg") 
    localcfgdefault_file= os.path.join(home_dir, "cluster-tools.cfg")
    return globalcfgdefault_file, localcfgdefault_file, default_dir, home_dir

def get_defaultsenvkey():
    return "COMOONICS_CLUSTER_TOOLS_CFG" 
