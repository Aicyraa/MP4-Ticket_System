from datetime import datetime, timedelta
import pandas as pd

# ────────────────────────────────────────────────────────────────────────────
# ANSI color codes
# ────────────────────────────────────────────────────────────────────────────

CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# ────────────────────────────────────────────────────────────────────────────
# Terminal ver helpers
# ────────────────────────────────────────────────────────────────────────────


def print_message(message: str) -> None:
    """Display a general info message."""
    print(f"{CYAN}>>>  {message}{RESET}")


def print_error(message: str) -> None:
    """Display an error message."""
    print(f"{RED}>>>  ERROR: {message}{RESET}\n")


def print_success(message: str) -> None:
    """Display a success message."""
    print(f"{GREEN}>>>  {message}{RESET}")


def print_menu(menu_text: str) -> None:
    """Display a menu."""
    print(f"{YELLOW}{menu_text}{RESET}")


def display_durations(durations: list) -> None:
    """Display attendance durations."""
    if not durations:
        return

    print(f"\n{CYAN}>>> ATTENDANCE DURATIONS:{RESET}")
    for ticket_id, name, duration in durations:
        print(f"{CYAN}  Ticket {ticket_id} | {name}: {duration}{RESET}")


def display_violations(violations: list) -> None:
    """Display rule violations."""
    if not violations:
        print_message("No rule violations detected!")
        return

    print(f"\n{RED}>>> RULE VIOLATIONS:{RESET}")
    for ticket_id, name, violation_type in violations:
        print(f"{RED}  Ticket {ticket_id} | {name}: {violation_type}{RESET}")


# ────────────────────────────────────────────────────────────────────────────
# Streamlit ver helpers
# ────────────────────────────────────────────────────────────────────────────


def fmt(seconds):
    return str(timedelta(seconds=int(seconds)))


def build_df(concert):
    rows = []
    for rec in concert.record:
        end = rec["exitTime"] or datetime.now()
        dur = (end - rec["entryTime"]).total_seconds() if rec["entryTime"] else 0
        rows.append(
            {
                "Ticket": rec["ticketID"],
                "Name": rec["name"],
                "Entry": (
                    rec["entryTime"].strftime("%H:%M:%S") if rec["entryTime"] else "N/A"
                ),
                "Exit": (
                    rec["exitTime"].strftime("%H:%M:%S")
                    if rec["exitTime"]
                    else "Still inside"
                ),
                "Duration": fmt(dur),
                "Status": "Inside" if rec["exitTime"] is None else "Exited",
                "_dur_sec": dur,
                "_exit_dt": rec["exitTime"],
                "_entry_dt": rec["entryTime"],
            }
        )
    return pd.DataFrame(rows)
