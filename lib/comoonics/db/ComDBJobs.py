"""
Jobs as object to database persistence to a generic database

"""
# here is some internal information
# $Id: ComDBJobs.py,v 1.3 2008-07-30 13:04:24 marc Exp $
#
from comoonics.ComExceptions import ComException
from comoonics import ComLog
from datetime import datetime
from ComDBObject import DBObject

_actionobject_registry=dict()

def registerActionObject(_action, _class):
    _actionobject_registry[_action]=_class

def getActionObjectForJob(job):
    """ Factory function to create an Action Object"""
    return Action(job)
def getActionClassForAction(_action):
    """ Factory function to create an Action Object"""
    return _actionobject_registry[_action]

class JobException(ComException):
    errorcode=0
    errormessage="Unknown errror: %(value)s"
    def __init__(self, **kwds):
        for (key, value) in kwds.items():
            setattr(self, key, value)
        
    def __str__(self):
        return "%s" %(self.errormessage %self.__dict__)

class DBJobs(DBObject):
    """
    Implementation of jobs. To be queried from a database.
    There are methods to be executed on the given jobs like: doAction
    The following attribute have to be definied with their correspondence in the given tables:
    @id: Key for the job
    @name: the name of the job (optional)
    @action: a given action to be applied to the job. Such a job object is created later on
    @errorcode: the errorcode returned by the execution of the job (optional)
    @errormessage: a message corresponding to the error (optional)
    @creationtime: a timestamp for the creation of the job
    @starttime: the time the job is executed (initialy 0)
    @endtime: the time the job is ended (successfully or not) (initially 0)
    """
    COLUMNNAMES=["id", "name", "errorcode", "errormessage", "creationtime", "starttime", "endtime"]
    OPT_COLUMNNAMES=["name", "errorcode", "errormessage"]
    def __init__(self, **kwds):
        """
        Creates an instance of the jobs. The _schema attribute defines the schema of the table. It is a map with key as attribute as defined
        above and value as columnname or None. If the columnname is None it will not be used. This only holds for options.
        If @schema is None columnames are as sepecified above.
        """
        super(DBJobs, self).__init__(**kwds)

    def getDoJobs(self):
        """
        Return all jobs which are not yet done
        """
        _rs=self.selectQuery(select=self.schema["id"], From=getattr(self, "tablename"), where={self.schema["starttime"]:0, self.schema["endtime"]: 0})
        _jobs=list()
        _ids=_rs.fetch_row()
        while _ids:
            _job=DBJob(dbhandle=self.db, id=_ids[0][0])
            _jobs.append(_job)
            _ids=_rs.fetch_row()
        return _jobs
    
    def doJobs(self):
        """
        Executes the specified action for the job. For this an action implementation has to be found.
        """
        for _job in self.getDoJobs():
            _job.doAction()
    
class DBJob(DBObject):
    """
    An abstrace job implementation the is not able to do any action.
    Attributes are as defined by the DBConnection and an ID defining the job and the schema.
    """
    COLUMNNAMES=["id", "name", "errorcode", "errormessage", "creationtime", "starttime", "endtime"]
    OPT_COLUMNNAMES=["name", "errorcode", "errormessage"]
    def __init__(self, **kwds):
        super(DBJob, self).__init__(**kwds)
        
    def __str__(self):
        return "Job{id: %u, created: %s, started: %s, ended: %s}" %(self.id, self.creationtime, self.starttime, self.endtime)
    
    def doAction(self):
        """
        Executes the action found with the given name in the global action repository.
        """
        self._fromDB()
        self.setStartTime()
        self.logger.info("Executing job %s at %s" %(self, self.starttime))
        self.errorcode=0
        try:
            _action=Action(dbhandle=self.db, job=self)
            _action.doAction()
            self.errormessage="Successfully executed job %(job)s at %(endtime)s"
        except JobException, e:
            self.logger.error(e)
            ComLog.debugTraceLog(self.logger)
            self.errorcode=e.errorcode
            self.errormessage=e.__str__()
            
        self.setEndTime()
        self.errormessage=self.errormessage %{"job": self, "starttime": self.starttime, "endtime": self.endtime}
        self.logger.info(self.errormessage)
            
    def setStartTime(self):
        self.starttime=datetime.now()
    def setEndTime(self):
        self.endtime=datetime.now()

class NoActionObjectFoundException(ComException): pass
class UnsupportedActionMetadataException(ComException): pass

class Action(object):
    def GetJobFromParams(*args, **kwds):
        _job=None
        if len (args) > 0 and isinstance(args[0], DBJob):
            _job=args[0]
        if kwds.has_key("job") and isinstance(kwds["job"], DBJob):
            _job=kwds["job"]
        return _job
    GetJobFromParams=staticmethod(GetJobFromParams)
        
    def __new__(cls, *args, **kwds):
        _job=Action.GetJobFromParams(*args, **kwds)
        if _job:
            if _actionobject_registry.has_key(_job.action):
                cls=getActionClassForAction(_job.action)
            else:
                raise NoActionObjectFoundException("Could not find action object for action: "+_job.action+". Use registry to register.")
            return object.__new__(cls, args, kwds)
        else:
            raise UnsupportedActionMetadataException("Unsupported ActionMetadata for constructor: %s. The action must be given a DBJob as first argument or a jobobject with job as keyword." %(args[0]))
    
    def __init__(self, *params, **kwds):
        if len (params) > 0 and isinstance(params[0], DBJob):
            _job=params[0]
        if kwds.has_key("job") and isinstance(kwds["job"], DBJob):
            _job=kwds["job"]
        self.jobid=_job.id
        self.params=list()        
        for _param in params:
            self.params.append(_param)
        for key in kwds.keys():
            if not hasattr(self, key):
                setattr(self, key, kwds[key])
            
    def doAction(self):
        """
        Abstract method that would execute the action
        """
        print "Action: %s" %self.__class__.__name__

class DBJob2Action(DBObject):
    COLUMNNAMES=["id", "jobid", "actionid"]
    OPT_COLUMNNAMES=["id"]
    def __init__(self, *params, **kwds):
        super(DBJob2Action, self).__init__(*params, **kwds)
        if not hasattr(self, "tablename"):
            self.tablename="jobs2actions"
        self.id=self.job.id

class DBAction(Action, DBObject):
    COLUMNNAMES=["id", "key", "value"]
        
    def __init__(self, *params, **_kwds):
        _comp=DBJob2Action(*params, **_kwds)
        if hasattr(_comp, "actionid"):
            _actionid=_comp.actionid
            _kwds["id"]=_actionid
        Action.__init__(self, *params, **_kwds)
        DBObject.__init__(self, *params, **_kwds)
        if not hasattr(self, "tablename"):
            self.tablename="actions"

    def doAction(self):
        """
        Abstract method that would execute the action
        """
        self.logger.debug("Action: %s, test: %s" %(self.__class__.__name__, self.test)) 

def test():
    try: 
        raise JobException(value="test123")
    except JobException, je:
        print je

if __name__=="__main__":
    test()

########################
# $Log: ComDBJobs.py,v $
# Revision 1.3  2008-07-30 13:04:24  marc
# bugfix in weired exception
#
# Revision 1.2  2008/03/03 08:32:08  marc
# - fixed bug where data where not read from db
# - more detailed error messages
#
# Revision 1.1  2008/02/28 14:19:23  marc
# initial revision
#
