"""
Email service for sending verification codes
Supports Gmail SMTP, SendGrid, and AWS SES
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import requests

load_dotenv()

EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'gmail').lower()
EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@cryptosense.app')
EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'CryptoSense DSS')

class EmailService:
    """Base email service"""
    
    @staticmethod
    def send_verification_email(email: str, code: str) -> bool:
        """Send verification code email"""
        if EMAIL_PROVIDER == 'gmail':
            return GmailService.send(email, code)
        elif EMAIL_PROVIDER == 'sendgrid':
            return SendGridService.send(email, code)
        elif EMAIL_PROVIDER == 'aws_ses':
            return AWSSESService.send(email, code)
        else:
            print(f"⚠️ Unknown email provider: {EMAIL_PROVIDER}")
            return False

    @staticmethod
    def send_password_reset_email(email: str, reset_link: str) -> bool:
        """Send password reset email"""
        if EMAIL_PROVIDER == 'gmail':
            return GmailService.send_reset(email, reset_link)
        elif EMAIL_PROVIDER == 'sendgrid':
            return SendGridService.send_reset(email, reset_link)
        elif EMAIL_PROVIDER == 'aws_ses':
            return AWSSESService.send_reset(email, reset_link)
        return False

class GmailService:
    """Gmail SMTP service"""
    
    @staticmethod
    def send(email: str, code: str) -> bool:
        """Send verification code via Gmail SMTP"""
        sender_email = os.getenv('GMAIL_EMAIL')
        sender_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not sender_email or not sender_password:
            print("❌ Gmail credentials not configured in .env")
            print("   Set GMAIL_EMAIL and GMAIL_APP_PASSWORD")
            return False
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "CryptoSense - Email Verification Code"
            message["From"] = f"{EMAIL_FROM_NAME} <{sender_email}>"
            message["To"] = email
            
            html = f"""\
            <html>
              <body style="font-family: 'IBM Plex Mono', monospace; background-color: #0b0c10; color: #c9d1d9;">
                <div style="max-width: 500px; margin: 0 auto; padding: 20px; background-color: #0d0e14; border: 1px solid #1e2030; border-radius: 8px;">
                  <h2 style="color: #e6edf3; font-family: 'DM Sans', sans-serif; margin-bottom: 20px;">₿ CryptoSense DSS</h2>
                  
                  <p style="color: #c9d1d9; margin-bottom: 20px;">Your email verification code is:</p>
                  
                  <div style="background-color: #0b0c10; padding: 20px; border-radius: 6px; text-align: center; margin: 20px 0;">
                    <h1 style="color: #f0b429; font-size: 2.5em; letter-spacing: 8px; margin: 0; font-family: 'DM Sans', sans-serif;">
                      {code}
                    </h1>
                  </div>
                  
                  <p style="color: #6b7280; font-size: 0.9em; margin: 20px 0;">
                    This code expires in <strong>10 minutes</strong>
                  </p>
                  
                  <p style="color: #6b7280; font-size: 0.85em; border-top: 1px solid #1e2030; padding-top: 20px;">
                    If you didn't request this code, please ignore this email.
                  </p>
                  
                  <p style="color: #4b5563; font-size: 0.75em; text-transform: uppercase; letter-spacing: 1px; margin-top: 30px;">
                    CryptoSense Decision Support System
                  </p>
                </div>
              </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            message.attach(part)
            
            # Send email
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, message.as_string())
            
            print(f"✓ Verification email sent to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Gmail SMTP error: {str(e)}")
            return False
    
    @staticmethod
    def send_reset(email: str, reset_link: str) -> bool:
        """Send password reset email"""
        sender_email = os.getenv('GMAIL_EMAIL')
        sender_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not sender_email or not sender_password:
            return False
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "CryptoSense - Reset Your Password"
            message["From"] = f"{EMAIL_FROM_NAME} <{sender_email}>"
            message["To"] = email
            
            html = f"""\
            <html>
              <body style="font-family: 'IBM Plex Mono', monospace; background-color: #0b0c10; color: #c9d1d9;">
                <div style="max-width: 500px; margin: 0 auto; padding: 20px; background-color: #0d0e14; border: 1px solid #1e2030; border-radius: 8px;">
                  <h2 style="color: #e6edf3; font-family: 'DM Sans', sans-serif; margin-bottom: 20px;">₿ CryptoSense DSS</h2>
                  
                  <p style="color: #c9d1d9; margin-bottom: 20px;">Click the link below to reset your password:</p>
                  
                  <p style="margin: 20px 0; text-align: center;">
                    <a href="{reset_link}" style="background-color: #f0b429; color: #0b0c10; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600;">
                      Reset Password
                    </a>
                  </p>
                  
                  <p style="color: #6b7280; font-size: 0.9em;">Link expires in 1 hour</p>
                </div>
              </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            message.attach(part)
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, message.as_string())
            
            print(f"✓ Password reset email sent to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Gmail error: {str(e)}")
            return False

class SendGridService:
    """SendGrid email service"""
    
    @staticmethod
    def send(email: str, code: str) -> bool:
        """Send verification code via SendGrid"""
        api_key = os.getenv('SENDGRID_API_KEY')
        
        if not api_key:
            print("❌ SendGrid API key not configured")
            print("   Set SENDGRID_API_KEY in .env")
            return False
        
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "personalizations": [
                    {
                        "to": [{"email": email}],
                        "subject": "CryptoSense - Email Verification Code"
                    }
                ],
                "from": {"email": os.getenv('SENDGRID_FROM_EMAIL', 'noreply@cryptosense.app'), "name": EMAIL_FROM_NAME},
                "content": [
                    {
                        "type": "text/html",
                        "value": f"""
                        <html>
                          <body style="font-family: 'IBM Plex Mono', monospace; background-color: #0b0c10; color: #c9d1d9;">
                            <div style="max-width: 500px; margin: 0 auto; padding: 20px; background-color: #0d0e14; border: 1px solid #1e2030; border-radius: 8px;">
                              <h2 style="color: #e6edf3; font-family: 'DM Sans', sans-serif;">₿ CryptoSense DSS</h2>
                              <p>Your verification code is:</p>
                              <h1 style="color: #f0b429; font-size: 2.5em; letter-spacing: 8px;">{code}</h1>
                              <p style="color: #6b7280;">This code expires in 10 minutes</p>
                            </div>
                          </body>
                        </html>
                        """
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 202:
                print(f"✓ Verification email sent to {email} (SendGrid)")
                return True
            else:
                print(f"❌ SendGrid error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ SendGrid error: {str(e)}")
            return False
    
    @staticmethod
    def send_reset(email: str, reset_link: str) -> bool:
        """Send password reset email via SendGrid"""
        api_key = os.getenv('SENDGRID_API_KEY')
        
        if not api_key:
            return False
        
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "personalizations": [
                    {
                        "to": [{"email": email}],
                        "subject": "CryptoSense - Reset Your Password"
                    }
                ],
                "from": {"email": os.getenv('SENDGRID_FROM_EMAIL', 'noreply@cryptosense.app'), "name": EMAIL_FROM_NAME},
                "content": [
                    {
                        "type": "text/html",
                        "value": f"""
                        <html>
                          <body>
                            <p>Click the link to reset your password:</p>
                            <p><a href="{reset_link}">Reset Password</a></p>
                          </body>
                        </html>
                        """
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=data)
            return response.status_code == 202
            
        except Exception as e:
            print(f"❌ SendGrid error: {str(e)}")
            return False

class AWSSESService:
    """AWS SES email service"""
    
    @staticmethod
    def send(email: str, code: str) -> bool:
        """Send verification code via AWS SES"""
        try:
            import boto3
            
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            client = boto3.client('ses', region_name=aws_region)
            
            html = f"""\
            <html>
              <body style="font-family: 'IBM Plex Mono', monospace; background-color: #0b0c10; color: #c9d1d9;">
                <div style="max-width: 500px; margin: 0 auto; padding: 20px; background-color: #0d0e14; border: 1px solid #1e2030; border-radius: 8px;">
                  <h2 style="color: #e6edf3;">₿ CryptoSense DSS</h2>
                  <p>Your verification code:</p>
                  <h1 style="color: #f0b429; font-size: 2.5em; letter-spacing: 8px;">{code}</h1>
                </div>
              </body>
            </html>
            """
            
            response = client.send_email(
                Source=os.getenv('AWS_SES_EMAIL', 'noreply@cryptosense.app'),
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': 'CryptoSense - Email Verification Code'},
                    'Body': {'Html': {'Data': html}}
                }
            )
            
            print(f"✓ Verification email sent to {email} (AWS SES)")
            return True
            
        except Exception as e:
            print(f"❌ AWS SES error: {str(e)}")
            return False
    
    @staticmethod
    def send_reset(email: str, reset_link: str) -> bool:
        """Send password reset via AWS SES"""
        try:
            import boto3
            
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            client = boto3.client('ses', region_name=aws_region)
            
            html = f"<p>Click to reset: <a href='{reset_link}'>Reset Password</a></p>"
            
            response = client.send_email(
                Source=os.getenv('AWS_SES_EMAIL', 'noreply@cryptosense.app'),
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': 'CryptoSense - Reset Your Password'},
                    'Body': {'Html': {'Data': html}}
                }
            )
            
            return True
            
        except Exception as e:
            print(f"❌ AWS SES error: {str(e)}")
            return False

# Easy function for imports
def send_verification_email(email: str, code: str) -> bool:
    """Send verification code to email"""
    return EmailService.send_verification_email(email, code)

def send_password_reset_email(email: str, reset_link: str) -> bool:
    """Send password reset link to email"""
    return EmailService.send_password_reset_email(email, reset_link)
