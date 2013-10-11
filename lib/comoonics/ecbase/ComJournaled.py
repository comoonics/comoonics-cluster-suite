"""Comoonics Journaled module


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComJournaled.py,v 1.1 2011-02-15 14:51:50 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ecbase/ComJournaled.py,v $

from comoonics import ComLog
import inspect

class JournaledObject:
   """
   Object for journaled all actions.
   Internally JournaledObject has a map of undomethods and references to objects that methods should be executed upon.
   If undo is called the journal stack is executed from top to buttom (LIFO) order.
   """
   __logStrLevel__ = "JournaledObject"

   class JournalEntry:
      """
      An entry in the journal
      """
      def __init__(self, *params):
         self.ref=params[0]
         self.method=params[1]
         if len(params) == 3:
            self.params=params[2]
         elif len(params) > 3:
            self.params=params[2:]
         else:
            self.params=None

   def __init__(self):
      self.__journal__=list()
      self.__undomap__=dict()

   def addToUndoMap(self, classname, methodname, undomethod):
      """
      Adds a new entry to the undomap. We add a 3 tuple to every undomap. Key is the methodname and undomethod and
      refobject are the values to be executed on replayJournal.
      """
      self.__undomap__[classname+"."+methodname]=undomethod

   def removeFromUndoMap(self, classname, methodname):
      """
      Removes a already added method from the undomap
      """
      if self.__undomap__.has_key(classname+"."+methodname):
         self.__undomap__.pop(classname+"."+methodname)

   def journal(self, *params):
      """
      Adds an entry to the journal list

      params - must be a list of at least 2 params (ref and methodname). Optionally the rest are parameters to the
             method
      """
      if len(params) == 3:
         self.__journal__.append(JournaledObject.JournalEntry(params[0], params[1], params[2]))
      elif len(params) >3:
         self.__journal__.append(JournaledObject.JournalEntry(params[0], params[1], params[2:]))
      else:
         self.__journal__.append(JournaledObject.JournalEntry(params[0], params[1]))

   def replayJournal(self):
      """
      replays the journal from top to buttom. The last inserted method first.
      """
      self.__journal__.reverse()
      for je in self.__journal__:
         ComLog.getLogger(JournaledObject.__logStrLevel__).debug("Journalentry: %s, %s" %(je.method, je.ref.__class__))
         undomethod=""
         try:
            if inspect.ismodule(je.ref):
               undomethod=self.__undomap__[str(je.ref.__name__+"."+je.method)]
            else:
               undomethod=self.__undomap__[str(je.ref.__class__.__name__+"."+je.method)]
            ComLog.getLogger(JournaledObject.__logStrLevel__).debug("Undomethod: %s(%s)" % (undomethod, je.params))
            if not je.params or (type(je.params)==list and len(je.params) == 0):
               # changed call of replay
               # __class__.__dict__[undomethod] does not work with inherited methods
               #je.ref.__class__.__dict__[undomethod](je.ref)
               getattr(je.ref,undomethod)()
            elif type(je.params)!=list and type(je.params)!=tuple:
               getattr(je.ref, undomethod)(je.params)
            elif len(je.params) == 1:
               #je.ref.__class__.__dict__[undomethod](je.ref, je.params[0])
               getattr(je.ref,undomethod)(je.params[0])
            else:
               #je.ref.__class__.__dict__[undomethod](je.ref, je.params)
               getattr(je.ref,undomethod)(*je.params)
         except Exception, e:
            ComLog.getLogger(JournaledObject.__logStrLevel__).warn("Caught exception e during journal replay of method %s => %s on %s: %s" % (je.method, undomethod, je.ref.__class__.__name__, e))
            ComLog.debugTraceLog(ComLog.getLogger(JournaledObject.__logStrLevel__))
   def commitJournal(self):
      """
      commits the journal, i.e. deletes all journal entries
      """
      self.__journal__=[]
