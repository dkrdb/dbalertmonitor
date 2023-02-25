import itertools
from collections import deque
import subprocess

# Define the name of the file that contains the list of alertlog directories
alert_filename = "alert_location.conf"

# Define the name of the file that contains the list of errors
alert_error = "alert_error.conf"

# Define sender and recipient information
sender = "it-monitor@itexample.com"
recipient  = "dbagroup@itexample.com"

with open(alert_filename, "r") as f:
    # Reads the lines of the file and removes newline characters
    alert_filename_list = [line.strip().split() for line in f.readlines()]

with open(alert_error, "r") as f:
    # Reads the lines of the file and removes newline characters
    alert_error_list = [line.strip() for line in f.readlines()]

for alert in alert_filename_list:
    server = alert[0]
    instance = alert[1]
    alert_location_file = alert[2]
    # Opens the alert log file and searches for errors listed in the alert_error.txt file
    with open(alert_location_file, "r", encoding="iso-8859-1") as a:
        # Reads the last 100 lines of the file
        last_lines = deque(maxlen=100)
        for line in itertools.islice(reversed(list(a)), 0, 100):
            last_lines.appendleft(line.strip())

        for i, line in enumerate(last_lines):
            if any(error in line for error in alert_error_list):
                # If the error is found, prepares the email body
                subject = f"Error found on server {server}, instance {instance}"
                message = f"""\
                Hi team,

                An error was found on server {server}, instance {instance}:

                Log file: {alert_location_file}
                Line {i-1}: {last_lines[i-2]}
                Line {i}: {line}
                Line {i+1}: {last_lines[i+1]}

                Best regards,
                Vale DBA Monitor"""

                # Command that calls mailx with the email information
                cmd = f'echo "{message}" | mailx -s "{subject}" -a {alert_location_file} -r {sender} {recipient}'

                # Sends the email
                try:
                    subprocess.run(cmd, shell=True, check=True)
                    print("Email sent successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"An error occurred while sending the email: {e}")
                break