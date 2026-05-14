from datetime import timedelta 

class Concert:
   def __init__(self, **dur):
      # Converts int into time (minutes), eto basihan natin sa ibang functions
      self.duration = timedelta(hours=dur['hour'], minutes=dur['mins'], seconds=dur['secs'])
   
   