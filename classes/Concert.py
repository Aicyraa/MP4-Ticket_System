from datetime import datetime, timedelta
from .Record import Record
from utils import (
    print_input,
    print_message,
    print_success,
    print_error,
    print_header,
    display_durations,
    display_violations,
    extract_seconds,
    print_summary_counts,
    print_record_table,
    print_attendee_table,
    print_duration_stats,
    print_violation_summary,
)


class Concert(Record):
    def __init__(self, **dur):
        super().__init__()
        self.duration = timedelta(hours=dur["hours"], minutes=dur["mins"], seconds=dur["secs"])

    def pushAttendee(self, name: str = None):
        if name is None:
            name = print_input('Enter attendee name (or press Enter to cancel): ').strip()
        if not name:
            return print_error("Push cancelled: name cannot be empty.")
        existing_ids = [a.get("ticketID", 0) for a in self.record]
        next_ticket = max(existing_ids) + 1 if existing_ids else 1
        attendee = {"ticketID": next_ticket, "name": name, "entryTime": datetime.now(), "exitTime": None}

        self.attendees.append(attendee)
        self.record.append(attendee)
        print_success(f"{name} entered. Ticket: {next_ticket}")
        return attendee

    def popAttendee(self):
        if self._isAttendanceEmpty():
            return print_error("No attendees inside the venue.")
        attendee = self.attendees.pop()
        attendee["exitTime"] = datetime.now()
        ticket_id, name, _, exit_time = self._getAttendeeData(attendee)
        print_success(f"{name} exited the venue. Ticket: {ticket_id} | Exit Time: {exit_time.strftime('%H:%M:%S')}")
        return attendee

    def peekLastAttendee(self):
        if self._isAttendanceEmpty():
            return print_error("There are no people inside.")
        ticket_id, name, entry_time, _ = self._getAttendeeData(self.attendees[-1])
        print_message(f"Last Attendee: ID: {ticket_id}, Name: {name}, Entry Time: {entry_time.strftime('%H:%M:%S')}")
        return self.attendees[-1]

    def getAttendanceDuration(self):
        if self._isRecordEmpty():
            return print_error("There are no attendees on record.")
        
        durations = []
        for rec in self.record:
            end = rec["exitTime"] or datetime.now()
            delta = timedelta(seconds=int((end - rec["entryTime"]).total_seconds()))
            durations.append((rec["ticketID"], rec["name"], delta))
        
        print_header("Attendance Durations")
        display_durations(durations)
        return durations

    def detectRuleViolations(self):
        if self._isRecordEmpty():
            return print_error("There are no attendees on record.")
        
        violations = []
        for rec in self.record:
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
        if self._isAttendanceEmpty():
            return print_error("Venue is empty.")
        print_header("Current Attendees")
        print_attendee_table(self.attendees)

    def generateAttendanceReport(self):
        if self._isRecordEmpty():
            return print_error("No attendance data available for the report.")

        total       = len(self.record)
        still_inside = sum(1 for r in self.record if r["exitTime"] is None)
        exited      = total - still_inside

        duration_tuples  = self.getAttendanceDuration()
        dur_secs         = extract_seconds(duration_tuples) if duration_tuples else []
        violation_tuples = self.detectRuleViolations()

        print_header("Concert Attendance Report")
        print_summary_counts(total, still_inside, exited)
        print_record_table(self.record)
        print_duration_stats(dur_secs)
        print_violation_summary(violation_tuples)

        return {
            "total":        total,
            "still_inside": still_inside,
            "exited":       exited,
            "durations":    dur_secs,
            "violations":   violation_tuples,
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _isAttendanceEmpty(self):
        return not self.attendees
    
    def _isRecordEmpty(self):
        return not self.record

    def _getAttendeeData(self, attendee):
        return (attendee["ticketID"], attendee["name"], attendee["entryTime"], attendee["exitTime"])