import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email(response_text, to_email):
    msg = EmailMessage()
    msg["Subject"] = "API Response"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(response_text)

    # Gmail SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

