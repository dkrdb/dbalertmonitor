This Python code searches for errors in a list of alert log files in Linux environments and sends an email to a specified recipient when an error is found.

The main program (checkalertlog/bin/check_logfiles.py) reads a list of alert log file locations (checkalertlog/conf/alert_location.conf) and a list of errors (checkalertlog/conf/alert_error.conf). It then opens each alert log file and searches for the specified errors in the last 10 lines of each alert log file. If an error is found, the program composes an email message containing information about the error, including the file name and the line where the error occurred.

Finally, the program sends the email to the specified recipient using the mailx command and generate a report (checkalertlog/report/logfilerpt.csv) of each email sent.

It is assumed that the smtp email infrastructure, such as sendmail, is in place in order to send emails.

For scheduling purposes, the execution can be accomplished using 'crontab' as follows:

crontab -l
========== Monitoring alert log Running every 5 minutes ==========

*/5 * * * * /usr/bin/python3 <$path>/checkalertlog/bin/check_logfiles.py 1>/dev/null 2>&1
