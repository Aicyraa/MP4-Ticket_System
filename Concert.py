import datetime as dt


class Concert:
    def __init__(self, **dur):
        # Converts int into time (minutes), eto basihan natin sa ibang functions
        self.duration = dt.timedelta(
            hours=dur["hours"], minutes=dur["mins"], seconds=dur["secs"]
        )
        # Stack
        self.attendees = []

    def pushAttendee(self):
        name = input("Enter your name: ")

        next_ticket = self.attendees[-1]["ticket"] + 1 if self.attendees else 1

        new_attendee = {
            "ticket": next_ticket,
            "name": name,
            "entryTime": dt.datetime.now(), 
            "exitTime": None,
        }

        already_in = next(
            (a for a in self.attendees if a["name"] == name and a["entryTime"] is not None),
            None
        )

        if already_in:
            print(f"[⤐ ENTRY DENIED ❌ ⬷] {name} has already entered. Ticket #{already_in['ticket']}.")
            return None

        self.attendees.append(new_attendee)
        print(f"[⤐ ENTRY SUCCESS ✅ ⬷] Welcome, {name}! Ticket #{next_ticket} | Entry: {new_attendee['entryTime'].strftime('%H:%M:%S')}")
        return new_attendee

    def popAttendee(self):

        if len(self.attendees) == 0:
            print("[⤐ EXIT DENIED ❌ ⬷] No attendees inside the venue.")
            return

        attendee = self.attendees.pop()
        attendee.exit_time = dt.now()

        print(
            f"[⤐ EXIT SUCCESS ✅ ⬷] '{attendee.name}' exited the venue. "
            f"Ticket: {attendee.ticket_id} | "
            f"Exit Time: {attendee.exit_time.strftime('%H:%M:%S')}"
        )

    def peekLastAttendee(self):
        pass

    def getAttendanceDuration(self):
        pass

    def detectRuleViolations(self):
        pass

    def displayAttendees(self):
        if not self.attendees:
            print("Venue is empty.")
            return

        print(f"\n{'#':<5} {'Ticket':<12} {'Name':<15} {'Entry Time'}")
        print("-" * 50)
        for i, a in enumerate(reversed(self.attendees)):
            tag = " <- TOP" if i == 0 else ""
            print(f"{i+1:<5} {a['ticket']:<12} {a['name']:<15} {a['entryTime'].strftime('%I:%M %p')}{tag}")
        print("-" * 50)
        print(f"Total inside: {len(self.attendees)}\n")


    def generateAttendanceRep(self):
        pass
    
  