from classes import Concert
from utils import print_input, print_message, print_error, print_menu, print_success


def session():
    while True:
        print_menu("""
        Welcome to the Concert Attendance System!
          (0) Exit
          (1) Create another concert entry.
        """)
        try:
            choice = int(print_input(""))
            if choice in (0, 1):
                return choice
            print_error(f"{choice} is not a valid input!")
        except ValueError:
            print_error("Input must be an integer!")


def initConcert():
    while True:
        try:
            # Converts string input into a list of numbers
            duration = list(map(int, print_input("Enter concert duration in this format (hours minutes seconds):  ").split(" ")))
            if len(duration) != 3:
                print_error("Please enter exactly 3 values: hours minutes seconds")
                continue
            hours, mins, secs = duration
            CONCERT = Concert(hours=hours, mins=mins, secs=secs)
            print_success(f"Concert Duration: {CONCERT.duration}")
            return CONCERT
        except ValueError:
            print_error("Duration must be integers only!")


def operateConcert(concert):
    while True:
        print_menu("""
        What would you like to do?
          (0) Exit
          (1) Push attendee
          (2) Pop attendee
          (3) Peek the last attendee
          (4) Get attendance duration
          (5) Detect rule violations
          (6) Display attendees
          (7) Generate attendance report
        """)
        try:
            choice = int(print_input(""))
        except ValueError:
            print_error("Input must be an integer!")
            continue

        if choice == 0: break
        elif choice == 1: concert.pushAttendee()
        elif choice == 2: concert.popAttendee()
        elif choice == 3: concert.peekLastAttendee()
        elif choice == 4: concert.getAttendanceDuration()
        elif choice == 5: concert.detectRuleViolations()
        elif choice == 6: concert.displayAttendees()
        elif choice == 7: concert.generateAttendanceReport()
        else: print_error(f"{choice} is not a valid input!")


if __name__ == "__main__":
    while True:
        action = session()
        if action == 0:
            # Exit
            print_message("Goodbye! See you at the next concert!")
            break
        else:
            # Init concert class then pass it to operateConcert
            print_message("Setting up a new concert entry...")
            operateConcert(initConcert())
