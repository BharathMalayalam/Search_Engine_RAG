import smtplib
from email.mime.text import MIMEText
import os

def email_agent(to_email, content):
    msg = MIMEText(content)
    msg["Subject"] = "Bharath Email"
    msg["From"] = os.getenv("EMAIL")
    msg["To"] = to_email

    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    
    # Writing debug to a file so it's not lost on clear and I can verify it
    with open("smtp_debug.txt", "w") as f:
        f.write(f"EMAIL='{email}'\n")
        f.write(f"PASSWORD_LEN={len(password) if password else 0}\n")
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email, password)
            server.send_message(msg)
        with open("smtp_debug.txt", "a") as f:
            f.write("DEBUG: [SUCCESS] Email sent successfully.\n")
    except Exception as e:
        with open("smtp_debug.txt", "a") as f:
            f.write(f"DEBUG: [FAILURE] {str(e)}\n")
        print(f"DEBUG: Email sending failed: {e}")