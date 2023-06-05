import smtplib
from email.mime.text import MIMEText
import pandas as pd

def read_contacts():
    connects=pd.read_csv(r"emails_dummy.csv")
    emails_list=connects.emails.tolist()
    # print(emails_list)
    return emails_list

def send_email_tolist(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()

def send_email_multiple(subject, body, sender, recipients, password):
    for recipient in recipients:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipient, msg.as_string())
        smtp_server.quit()
# https://myaccount.google.com/apppasswords




sender=input('Enter your Email:')
password=input('Enter your Password:')
subject=input('Enter Subject: ')
body=input('Enter Message Body: ')
recipients=read_contacts()
send_email_multiple(subject, body, sender, recipients, password)
