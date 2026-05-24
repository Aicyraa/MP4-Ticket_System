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
