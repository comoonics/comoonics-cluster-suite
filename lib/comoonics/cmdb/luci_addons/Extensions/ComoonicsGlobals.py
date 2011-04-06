"""
Just globals hopefully go away in future
"""
import logging
from comoonics import ComLog

mysqlserver="localhost"
mysqluser="hoi"
mysqlpassword="Digital"
mysqldatabase="hoi_config"

ComLog.setLevel(logging.DEBUG)
mylog=logging.getLogger("ComoonicsCMDB")
mylog.setLevel(logging.DEBUG)

installed_ids=[ "installed1", "installed2" ]
notinstalled_ids=[ "notinstalled1", "notinstalled2" ]
log_cols=["logtimestamp", "loglevel", "logsource", "logmsg", "logexecinfo"]
details={"master": ["OnlyDiffs", "OnlyNotInstalled", "AlsoInstalled"],
        "source":  ["OnlyDiffs", "OnlyNotInstalled", "AlsoInstalled"],
        "category":["OnlyDiffs", "OnlyNotInstalled", "AlsoInstalled"]}
default_details={"master":  [ False, False, True ],
                "source":   [False, False, True],
                "category": [False, False, True] }

#################
# $Log$
