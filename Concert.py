from datetime import timedelta 

class Concert:
   def __init__(self, **dur):
      # Converts int into time (minutes), eto basihan natin sa ibang functions
      self.duration = timedelta(hours=dur['hours'], minutes=dur['mins'], seconds=dur['secs'])
      # Stack
      self.attendees = []
   
   def pushAttendee(self):
      pass
   
   def popAttendee(self):

      if len(self.attendees) == 0:
         print("[⤐ EXIT DENIED ❌ ⬷] No attendees inside the venue.")
         return

      attendee = self.attendees.pop()
      attendee.exit_time = datetime.now()

      print(f"[⤐ EXIT SUCCESS ✅ ⬷] '{attendee.name}' exited the venue. "
         f"Ticket: {attendee.ticket_id} | "
         f"Exit Time: {attendee.exit_time.strftime('%H:%M:%S')}")
   
   def peekLastAttendee(self):
      pass
   
   def getAttendanceDuration(self):
      pass
   
   def detectRuleViolations(self):
      pass
   
   def displayAttendees(self):
      pass
   
   def generateAttendanceRep(self):
      pass