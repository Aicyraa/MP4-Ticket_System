def generateAttendanceReport(self):
    if not self.record:
        return print_error("No attendance data available for the report.")

    total = len(self.record)
    still_inside = sum(1 for r in self.record if r["exitTime"] is None)
    exited = total - still_inside

    durations = []
    for rec in self.record:
        if rec["entryTime"] is None:
            continue
        end = rec["exitTime"] or datetime.now()
        durations.append((end - rec["entryTime"]).total_seconds())

    def fmt(sec):
        return str(timedelta(seconds=int(sec)))

    sep = "=" * 55
    print(f"\n{sep}")
    print("        CONCERT ATTENDANCE REPORT")
    print(sep)

    print(f"\n  Total registered : {total}")
    print(f"  Still inside     : {still_inside}")
    print(f"  Already exited   : {exited}")

    print(f"\n  {'Ticket':<8} {'Name':<20} {'Entry':<12} {'Exit'}")
    print("  " + "-" * 50)
    for rec in self.record:
        entry = rec["entryTime"].strftime("%H:%M:%S") if rec["entryTime"] else "N/A"
        exit_ = rec["exitTime"].strftime("%H:%M:%S") if rec["exitTime"] else "Still inside"
        print(f"  {rec['ticketID']:<8} {rec['name']:<20} {entry:<12} {exit_}")

    if durations:
        print(f"\n  Average stay  : {fmt(sum(durations) / len(durations))}")
        print(f"  Longest stay  : {fmt(max(durations))}")
        print(f"  Shortest stay : {fmt(min(durations))}")

    violations = []
    for rec in self.record:
        if rec["entryTime"] is None:
            continue
        end = rec["exitTime"] or datetime.now()
        attended = end - rec["entryTime"]
        if attended > self.duration:
            violations.append(f"  Ticket {rec['ticketID']} | {rec['name']}: Overstay")
        elif rec["exitTime"] and attended < self.duration:
            violations.append(f"  Ticket {rec['ticketID']} | {rec['name']}: Early Exit")

    print(f"\n  Violations ({len(violations)} found)")
    for v in violations:
        print(v)
    if not violations:
        print("  None detected.")

    print(f"\n{sep}\n")