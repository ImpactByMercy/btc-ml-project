# Email Service Setup Guide

CryptoSense DSS now has a production-ready email service that supports multiple providers.

## Quick Start - Gmail (Development)

### 1. Enable 2-Factor Authentication

- Go to [myaccount.google.com](https://myaccount.google.com)
- Click **Security** in the left menu
- Enable **2-Step Verification**

### 2. Generate App Password

- Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
- Select **Mail** and **Windows Computer** (or your device)
- Click **Generate**
- Copy the 16-character password

### 3. Update .env

```env
EMAIL_PROVIDER=gmail
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### 4. Test

```bash
cd backend
python app.py
# Register and login - you should receive an email!
```

---

## Production Setup

### Option 1: SendGrid (Recommended)

**Advantages:**

- Free tier: 100 emails/day
- Reliable delivery
- Great documentation
- Easy API

**Setup:**

1. **Create SendGrid Account**
   - Go to [sendgrid.com](https://sendgrid.com)
   - Sign up for free
   - Verify email and domain

2. **Get API Key**
   - Dashboard → API Keys
   - Create new key with "Mail Send" permission
   - Copy the key

3. **Update .env**

```env
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxx...
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

4. **Install requests** (already in requirements.txt)

---

### Option 2: AWS SES

**Advantages:**

- Cheapest option (~$0.10 per 1,000 emails)
- Integrates with AWS ecosystem
- Very scalable

**Setup:**

1. **Create AWS Account** (if you don't have one)
   - Go to [aws.amazon.com](https://aws.amazon.com)

2. **Enable SES Service**
   - Go to Simple Email Service (SES)
   - Verify your domain or email
   - Request production access

3. **Create IAM User**
   - IAM → Users → Add user
   - Attach "AmazonSesSendingAccess" policy
   - Create access key

4. **Install boto3**

```bash
pip install boto3
```

5. **Update .env**

```env
EMAIL_PROVIDER=aws_ses
AWS_REGION=us-east-1
AWS_SES_EMAIL=noreply@yourdomain.com
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=xxx...
```

---

### Option 3: Gmail SMTP (Production)

**Advantages:**

- Works immediately
- No setup needed

**Limitations:**

- Rate limited
- Not recommended for high volume

**Setup:**
Same as development setup above, just use your production Gmail account.

---

## Switching Providers

Just change `EMAIL_PROVIDER` in `.env`:

```env
# To use SendGrid
EMAIL_PROVIDER=sendgrid

# To use AWS SES
EMAIL_PROVIDER=aws_ses

# To use Gmail
EMAIL_PROVIDER=gmail
```

---

## Testing Email Service

```python
# In Python shell
from backend.email_service import send_verification_email

# Send test email
send_verification_email('test@example.com', 'ABC123')
```

---

## Troubleshooting

### Gmail: "Email and password not accepted"

- Make sure 2FA is enabled
- Use app password, not regular password
- Check app password is correct

### SendGrid: "Permission denied"

- Check API key is correct
- Check key has "Mail Send" permission
- Check FROM email is verified

### AWS SES: "Email address not verified"

- Go to SES → Verified identities
- Verify your domain or email
- Request production access (if in sandbox)

### All: "Email not sent"

- Check .env file has correct values
- Check EMAIL_PROVIDER is correct
- Check backend logs for errors
- Restart backend after .env changes

---

## Email Templates

All emails use the CryptoSense dark theme and match the UI design.

**Verification Code Email:**

- Dark background (#0b0c10)
- Yellow code highlight (#f0b429)
- Professional styling
- 10-minute expiration notice

**Password Reset Email:**

- Same dark theme
- Click-able reset button
- 1-hour expiration link

---

## Next Steps

1. **Choose a provider** (Gmail for dev, SendGrid/AWS for production)
2. **Configure .env** with credentials
3. **Restart backend**
4. **Test registration flow** - email should arrive!

Questions? Check the provider's documentation:

- [SendGrid Docs](https://docs.sendgrid.com)
- [AWS SES Docs](https://docs.aws.amazon.com/ses/)
- [Gmail SMTP Info](https://support.google.com/accounts/answer/185833)
