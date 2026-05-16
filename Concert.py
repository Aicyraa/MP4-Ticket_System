from datetime import timedelta 

class Concert:
   def __init__(self, **dur):
      # Converts int into time (minutes), eto basihan natin sa ibang functions
      self.duration = timedelta(hours=dur['hours'], minutes=dur['mins'], seconds=dur['secs'])
      # Stack
      self.attendees = []
   
   def pushAttendee():
      pass
   
   def popAttendee():
      pass
   
   def peekLastAttendee():
      pass
   
   def getAttendanceDuration():
      pass
   
   def detectRuleViolations():
      pass
   
   def displayAttendees():
      pass
   
   def generateAttendanceRep():
      pass
   
