import os
import requests

def send_verification_email(email, code):
    print(f'Verification code for {email}: {code}')
    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('SENDGRID_FROM_EMAIL', 'mercymusyoka020@gmail.com')
    if not api_key:
        print('No SendGrid API key found')
        return True
    try:
        response = requests.post(
            'https://api.sendgrid.com/v3/mail/send',
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={
                'personalizations': [{'to': [{'email': email}], 'subject': 'CryptoSense Verification Code'}],
                'from': {'email': from_email, 'name': 'CryptoSense DSS'},
                'content': [{'type': 'text/html', 'value': f'<h2 style="color:#f0b429">{code}</h2><p>Your CryptoSense DSS verification code. Expires in 10 minutes.</p>'}]
            }
        )
        if response.status_code == 202:
            print(f'Email sent to {email} via SendGrid')
        else:
            print(f'SendGrid error: {response.status_code} {response.text}')
    except Exception as e:
        print(f'Email error: {e}')
    return True

def send_password_reset_email(email, reset_link):
    print(f'Password reset for {email}: {reset_link}')
    return True
