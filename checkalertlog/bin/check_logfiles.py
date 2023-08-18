import csv
import subprocess
from collections import deque
from datetime import datetime
import os.path

# Define the name of the file that contains the list of alertlog directories
alert_filename = "$SCRIPT_PATH/checkalertlog/conf/alert_location.conf"

# Define the name of the file that contains the list of errors
alert_error = "$SCRIPT_PATH/checkalertlog/conf/alert_error.conf"

# Define sender and recipient information
sender = "example@example.com"
recipient  = "example@example.com"

# Define the name of the CSV file to store error information
csv_filename = "$SCRIPT_PATH/checkalertlog/report/logfilerpt.csv"

def get_last_position(logfile):
    try:
        with open(f"{logfile}.position", "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def update_last_position(logfile, position):
    with open(f"{logfile}.position", "w") as f:
        f.write(str(position))

# Check if the CSV file exists, and if not, create it with the header row
if not os.path.isfile(csv_filename):
    with open(csv_filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Error Code", "Date/Time", "Log File", "Server", "Instance"])

# Read alert_filename and alert_error lists
with open(alert_filename, "r") as f:
    alert_filename_list = [line.strip().split() for line in f.readlines()]

with open(alert_error, "r") as f:
    alert_error_list = [line.strip() for line in f.readlines()]

for alert in alert_filename_list:
    server = alert[0]
    instance = alert[1]
    alert_location_file = alert[2]

    # Get the last read position for this log file
    last_position = get_last_position(alert_location_file)

    # Opens the alert log file and searches for errors listed in the alert_error.txt file
    with open(alert_location_file, "r", encoding="iso-8859-1") as a:
        # Reads the last lines of the file since the last position
        a.seek(last_position)
        last_lines = deque(a, maxlen=10)

        for i, line in enumerate(last_lines):
            error_code = "Unknown"
            for error in alert_error_list:
                if error in line:
                    error_code = error
                    break

            if error_code != "Unknown":
                # If the error is found, prepares the email body
                subject = f"Error found on server {server}, instance {instance}"
                message = f"""
                Hi team,

                An error was found on server {server}, instance {instance}:

                Log file: {alert_location_file}
                {line}

                Best regards,
                DBA Monitor"""

                # Get the current date and time
                now = datetime.now()

                # Command that calls mailx with the email information
                cmd = f'echo "{message}" | mailx -s "{subject}" -r {sender} {recipient}'

                # Sends the email
                try:
                    subprocess.run(cmd, shell=True, check=True)
                    print("Email sent successfully.")

                    # Write the error information to the CSV file
                    with open(csv_filename, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([error_code, now.strftime("%Y-%m-%d %H:%M:%S"), alert_location_file, server, instance])

                    # Update the last position for this log file
                    update_last_position(alert_location_file, a.tell())

                except subprocess.CalledProcessError as e:
                    print(f"An error occurred while sending the email: {e}")
