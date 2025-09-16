import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

def send_reset_email(to_email, token):
    reset_link = f"https://fitnessdashboard.onrender.com/reset-password/{token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Password Reset Request"
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    html = f"""
    <html>
      <body>
        <p>Hello,<br><br>
           You requested a password reset. Click the link below:<br>
           <a href="{reset_link}">{reset_link}</a><br><br>
           If you didn’t request this, you can ignore this email.
        </p>
      </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())