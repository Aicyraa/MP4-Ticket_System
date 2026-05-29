from datetime import datetime, timedelta
import pandas as pd

# ────────────────────────────────────────────────────────────────────────────
# Terminal ver helpers
# ────────────────────────────────────────────────────────────────────────────


def print_message(message: str) -> None:
    """Display a general info message."""
    print(f">>>  {message}")


def print_error(message: str) -> None:
    """Display an error message."""
    print(f">>>  ERROR: {message}\n")


def print_success(message: str) -> None:
    """Display a success message."""
    print(f">>>  {message}")


def print_menu(menu_text: str) -> None:
    """Display a menu."""
    print(menu_text)


def display_durations(durations: list) -> None:
    """Display attendance durations."""
    if not durations:
        return

    print("\n>>> ATTENDANCE DURATIONS:")
    for ticket_id, name, duration in durations:
        print(f"  Ticket {ticket_id} | {name}: {duration}")


def display_violations(violations: list) -> None:
    """Display rule violations."""
    if not violations:
        print_message("No rule violations detected!")
        return

    print("\n>>> RULE VIOLATIONS:")
    for ticket_id, name, violation_type in violations:
        print(f"  Ticket {ticket_id} | {name}: {violation_type}")


# ────────────────────────────────────────────────────────────────────────────
# Streamlit ver helper
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
