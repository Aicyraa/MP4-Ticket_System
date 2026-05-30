from datetime import datetime, timedelta
import streamlit as st
import pandas as pd

# ────────────────────────────────────────────────────────────────────────────
# ANSI color codes
# ────────────────────────────────────────────────────────────────────────────

CYAN   = "\033[96m"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

# ────────────────────────────────────────────────────────────────────────────
# Terminal — core helpers
# ────────────────────────────────────────────────────────────────────────────

def print_input(message: str, prefix: bool = True) -> str:
    tag = ">  " if prefix else ""
    return input(f"{CYAN}{tag}{message}{RESET}")

def print_message(message: str, prefix: bool = True) -> None:
    tag = ">>>  " if prefix else ""
    print(f"{CYAN}{tag}{message}{RESET}")

def print_error(message: str, prefix: bool = True) -> None:
    tag = ">>>  ERROR: " if prefix else ""
    print(f"{RED}{tag}{message}{RESET}\n" if prefix else f"{RED}{message}{RESET}")

def print_success(message: str, prefix: bool = True) -> None:
    tag = ">>>  " if prefix else ""
    print(f"{GREEN}{tag}{message}{RESET}")

def print_menu(menu_text: str) -> None:
    print(f"{YELLOW}{menu_text}{RESET}")

def print_header(title: str) -> None:
    width = len(title) + 30
    sep = "=" * width
    print(f"{CYAN}\n{sep}\n{title.upper().center(width)}\n{sep}{RESET}")

def extract_seconds(duration_tuples: list) -> list:
    """Extract raw float seconds from [(ticketID, name, timedelta), ...]"""
    return [d.total_seconds() for _, _, d in duration_tuples]

def fmt(seconds) -> str:
    """Convert raw seconds → human-readable duration string."""
    return str(timedelta(seconds=int(seconds)))

# ────────────────────────────────────────────────────────────────────────────
# Terminal — structured print helpers
# ────────────────────────────────────────────────────────────────────────────

def print_summary_counts(total: int, still_inside: int, exited: int) -> None:
    print_success(f"\n  Total registered : {total}", prefix=False)
    print_success(f"  Still inside     : {still_inside}", prefix=False)
    print_success(f"  Already exited   : {exited}", prefix=False)

def print_record_table(record: list) -> None:
    print_message(f"\n  {'Ticket':<8} {'Name':<20} {'Entry':<12} {'Exit'}", prefix=False)
    print_message("  " + "-" * 50, prefix=False)
    for rec in record:
        entry = rec["entryTime"].strftime("%H:%M:%S") if rec["entryTime"] else "N/A"
        exit_ = rec["exitTime"].strftime("%H:%M:%S") if rec["exitTime"] else "Still inside"
        print_message(f"  {rec['ticketID']:<8} {rec['name']:<20} {entry:<12} {exit_}", prefix=False)

def print_attendee_table(attendees: list) -> None:
    print_message(f"\n  {'#':<5} {'Ticket':<12} {'Name':<15} {'Entry Time'}", prefix=False)
    print_message("  " + "-" * 45, prefix=False)
    for i, a in enumerate(reversed(attendees)):
        entry_time = a["entryTime"].strftime("%I:%M %p") if a["entryTime"] else "N/A"
        print_message(f"  {i+1:<5} {a['ticketID']:<12} {a['name']:<15} {entry_time}", prefix=False)
    print_message("  " + "-" * 45, prefix=False)
    print_success(f"  Total inside: {len(attendees)}\n")

def print_duration_stats(dur_secs: list) -> None:
    if not dur_secs:
        return
    print_success(f"\n  Average stay  : {fmt(sum(dur_secs) / len(dur_secs))}", prefix=False)
    print_success(f"  Longest stay  : {fmt(max(dur_secs))}", prefix=False)
    print_success(f"  Shortest stay : {fmt(min(dur_secs))}", prefix=False)

def print_violation_summary(violations: list) -> None:
    if violations:
        print_error(f"\n  Violations ({len(violations)} found)", prefix=False)
        for tid, name, vtype in violations:
            print_error(f"  Ticket {tid} : {name}: {vtype.title()}", prefix=False)
    else:
        print_success("\n  Violations (0 found)", prefix=False)
        print_success("  None detected.", prefix=False)

def display_durations(durations: list) -> None:
    if not durations:
        return
    for ticket_id, name, duration in durations:
        print_message(f"Ticket: {ticket_id} | {name}: {duration}", prefix=False)

def display_violations(violations: list) -> None:
    if not violations:
        print_message("No rule violations detected!")
        return
    for ticket_id, name, violation_type in violations:
        print_error(f"Ticket: {ticket_id} | {name}: {violation_type}", prefix=False)

# ────────────────────────────────────────────────────────────────────────────
# Streamlit helpers
# ────────────────────────────────────────────────────────────────────────────

def build_df(concert):
    rows = []
    for rec in concert.record:
        end = rec["exitTime"] or datetime.now()
        dur = (end - rec["entryTime"]).total_seconds() if rec["entryTime"] else 0
        rows.append({
            "Ticket":   rec["ticketID"],
            "Name":     rec["name"],
            "Entry":    rec["entryTime"].strftime("%H:%M:%S") if rec["entryTime"] else "N/A",
            "Exit":     rec["exitTime"].strftime("%H:%M:%S") if rec["exitTime"] else "Still inside",
            "Duration": fmt(dur),
            "Status":   "Inside" if rec["exitTime"] is None else "Exited",
            "_dur_sec": dur,
            "_exit_dt": rec["exitTime"],
            "_entry_dt": rec["entryTime"],
        })
    return pd.DataFrame(rows)

def metric_card(label, value, color=""):
    return (
        f'<div class="metric-card">'
        f'<div class="label">{label}</div>'
        f'<div class="value {color}">{value}</div>'
        f"</div>"
    )


def metric_row(*cards):
    st.markdown(
        f'<div class="metric-row">{"".join(cards)}</div>', unsafe_allow_html=True
    )


def box_title(title):
    st.markdown(f'<div class="box-title">{title}</div>', unsafe_allow_html=True)


def empty_state(icon, text):
    st.markdown(
        f'<div class="empty-state">'
        f'<div class="empty-icon">{icon}</div>'
        f'<p class="empty-text">{text}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )

