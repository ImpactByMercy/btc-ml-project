import os

def send_verification_email(email, code):
    print(f"Verification code for {email}: {code}")
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        sender_email = os.getenv("GMAIL_EMAIL")
        sender_password = os.getenv("GMAIL_APP_PASSWORD")
        if not sender_email or not sender_password:
            return True
        message = MIMEMultipart("alternative")
        message["Subject"] = "CryptoSense Verification Code"
        message["From"] = sender_email
        message["To"] = email
        html = f"<h1 style=color:#f0b429>{code}</h1><p>Your CryptoSense verification code</p>"
        message.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=5) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        print("Email sent")
    except Exception as e:
        print(f"Email skipped: {e}")
    return True

def send_password_reset_email(email, reset_link):
    print(f"Password reset for {email}: {reset_link}")
    return True
