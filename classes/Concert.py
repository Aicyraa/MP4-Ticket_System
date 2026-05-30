from datetime import datetime, timedelta
from .Record import Record
from utils import (
    print_message,
    print_success,
    print_error,
    print_header,
    display_durations,
    display_violations,
    fmt
)


class Concert(Record):
    def __init__(self, **dur):
        super().__init__()
        self.duration = timedelta(
            hours=dur["hours"], minutes=dur["mins"], seconds=dur["secs"]
        )

    def pushAttendee(self, name: str = None):
        """
        Push an attendee into the venue.
        - Terminal: calls input() when name is None.
        - Streamlit: pass name directly to skip input().
        """
        if name is None:
            name = input(">>>  Enter attendee name (or press Enter to cancel): ").strip()

        if not name:
            return print_error("Push cancelled: name cannot be empty.")

        existing_ids = [a.get("ticketID", 0) for a in self.record]
        next_ticket = max(existing_ids) + 1 if existing_ids else 1

        attendee = {
            "ticketID": next_ticket,
            "name": name,
            "entryTime": datetime.now(),
            "exitTime": None,
        }

        self.attendees.append(attendee)
        self.record.append(attendee)
        print_success(f"{name} entered. Ticket: {next_ticket}")
        return attendee

    def popAttendee(self):
        if self._isEmpty():
            return print_error("No attendees inside the venue.")

        attendee = self.attendees.pop()
        attendee["exitTime"] = datetime.now()
        ticket_id, name, _, exit_time = self._getAttendeeData(attendee)

        print_success(
            f"{name} exited the venue. "
            f"Ticket: {ticket_id} | "
            f"Exit Time: {exit_time.strftime('%H:%M:%S')}"
        )
        return attendee

    def peekLastAttendee(self):
        if self._isEmpty():
            return print_error("There are no people inside.")

        ticket_id, name, entry_time, _ = self._getAttendeeData(self.attendees[-1])
        print_message(
            f"Last Attendee: ID: {ticket_id}, Name: {name}, "
            f"Entry Time: {entry_time.strftime('%H:%M:%S')}"
        )
        return self.attendees[-1]

    def getAttendanceDuration(self):
        if not self.record:
            return print_error("There are no attendees on record.")

        durations = []
        for rec in self.record:
            if rec["entryTime"] is None:
                continue
            end = rec["exitTime"] or datetime.now()
            delta = timedelta(seconds=int((end - rec["entryTime"]).total_seconds()))
            durations.append((rec["ticketID"], rec["name"], delta))

        print_header("Attendance Durations")
        display_durations(durations)
        return durations

    def detectRuleViolations(self):
        if not self.record:
            return print_error("There are no attendees on record.")

        violations = []
        for rec in self.record:
            if rec["entryTime"] is None:
                continue

            end = rec["exitTime"] or datetime.now()
            attended = end - rec["entryTime"]

            if attended > self.duration:
                violations.append((rec["ticketID"], rec["name"], "overstay"))
            elif rec["exitTime"] and attended < self.duration:
                violations.append((rec["ticketID"], rec["name"], "early exit"))

        print_header("Rule Violations")
        display_violations(violations)
        return violations

    def displayAttendees(self):
        if self._isEmpty():
            return print_error("Venue is empty.")

        print_header("Current Attendees")
        print_message(f"\n  {'#':<5} {'Ticket':<12} {'Name':<15} {'Entry Time'}", prefix=False)
        print_message("  " + "-" * 45, prefix=False)
        for i, a in enumerate(reversed(self.attendees)):
            entry_time = a['entryTime'].strftime('%I:%M %p') if a['entryTime'] else "N/A"
            print_message(f"  {i+1:<5} {a['ticketID']:<12} {a['name']:<15} {entry_time}", prefix=False)
        print_message("  " + "-" * 45, prefix=False)
        print_success(f"  Total inside: {len(self.attendees)}\n")

    def generateAttendanceReport(self):
        if not self.record:
            return print_error("No attendance data available for the report.")

        total = len(self.record)
        still_inside = sum(1 for r in self.record if r["exitTime"] is None)
        exited = total - still_inside

        # getAttendanceDuration returns [(ticketID, name, timedelta), ...]
        # Extract raw seconds from each tuple for math (avg, min, max)
        duration_tuples = self.getAttendanceDuration()
        dur_secs = [d.total_seconds() for _, _, d in duration_tuples] if duration_tuples else []

        violation_tuples = self.detectRuleViolations()

        print_header("Concert Attendance Report")

        # ── Summary counts ────────────────────────────────────────────────────
        print_success(f"\n  Total registered : {total}", prefix=False)
        print_success(f"  Still inside     : {still_inside}", prefix=False)
        print_success(f"  Already exited   : {exited}", prefix=False)

        # ── Attendee table ────────────────────────────────────────────────────
        print_message(f"\n  {'Ticket':<8} {'Name':<20} {'Entry':<12} {'Exit'}", prefix=False)
        print_message("  " + "-" * 50, prefix=False)
        for rec in self.record:
            entry = rec["entryTime"].strftime("%H:%M:%S") if rec["entryTime"] else "N/A"
            exit_ = rec["exitTime"].strftime("%H:%M:%S") if rec["exitTime"] else "Still inside"
            print_message(f"  {rec['ticketID']:<8} {rec['name']:<20} {entry:<12} {exit_}", prefix=False)

        # ── Duration stats ────────────────────────────────────────────────────
        if dur_secs:
            print_success(f"\n  Average stay  : {fmt(sum(dur_secs) / len(dur_secs))}", prefix=False)
            print_success(f"  Longest stay  : {fmt(max(dur_secs))}", prefix=False)
            print_success(f"  Shortest stay : {fmt(min(dur_secs))}", prefix=False)

        # ── Violations ────────────────────────────────────────────────────────
        if violation_tuples:
            print_error(f"\n  Violations ({len(violation_tuples)} found)", prefix=False)
            for tid, name, vtype in violation_tuples:
                print_error(f"  Ticket {tid} | {name}: {vtype.title()}", prefix=False)
        else:
            print_success(f"\n  Violations (0 found)", prefix=False)
            print_success("  None detected.", prefix=False)

        print_message("")

        # Return structured data for Streamlit
        return {
            "total": total,
            "still_inside": still_inside,
            "exited": exited,
            "durations": dur_secs,
            "violations": violation_tuples,
        }

    # -------------------------
    # Private helpers
    # -------------------------

    def _isEmpty(self):
        return not self.attendees

    def _getAttendeeData(self, attendee):
        return (
            attendee["ticketID"],
            attendee["name"],
            attendee["entryTime"],
            attendee["exitTime"],
        )

  
    def generateAttendanceReport(self):
        if not self.record:
            return print_error("No attendance data available for the report.")
 
        total = len(self.record)
        still_inside = sum(1 for r in self.record if r["exitTime"] is None)
        exited = total - still_inside

        duration_tuples = self.getAttendanceDuration()
        dur_secs = [d.total_seconds() for _, _, d in duration_tuples] if duration_tuples else []
 
        violation_tuples = self.detectRuleViolations()
 
        print_header("Concert Attendance Report")
 
        # ── Summary counts ────────────────────────────────────────────────────
        print_success(f"\n  Total registered : {total}", prefix=False)
        print_success(f"  Still inside     : {still_inside}", prefix=False)
        print_success(f"  Already exited   : {exited}", prefix=False)
 
        # ── Attendee table ────────────────────────────────────────────────────
        print_message(f"\n  {'Ticket':<8} {'Name':<20} {'Entry':<12} {'Exit'}", prefix=False)
        print_message("  " + "-" * 50, prefix=False)
        for rec in self.record:
            entry = rec["entryTime"].strftime("%H:%M:%S") if rec["entryTime"] else "N/A"
            exit_ = rec["exitTime"].strftime("%H:%M:%S") if rec["exitTime"] else "Still inside"
            print_message(f"  {rec['ticketID']:<8} {rec['name']:<20} {entry:<12} {exit_}", prefix=False)
 
        # ── Duration stats ────────────────────────────────────────────────────
        if dur_secs:
            print_success(f"\n  Average stay  : {fmt(sum(dur_secs) / len(dur_secs))}", prefix=False)
            print_success(f"  Longest stay  : {fmt(max(dur_secs))}", prefix=False)
            print_success(f"  Shortest stay : {fmt(min(dur_secs))}", prefix=False)
 
        # ── Violations ────────────────────────────────────────────────────────
        if violation_tuples:
            print_error(f"\n  Violations ({len(violation_tuples)} found)", prefix=False)
            for tid, name, vtype in violation_tuples:
                print_error(f"  Ticket {tid} | {name}: {vtype.title()}", prefix=False)
        else:
            print_success(f"\n  Violations (0 found)", prefix=False)
            print_success("  None detected.", prefix=False)
 
        print_message("")
 
        # Return structured data for Streamlit
        return {
            "total": total,
            "still_inside": still_inside,
            "exited": exited,
            "durations": dur_secs,
            "violations": violation_tuples,
        }
