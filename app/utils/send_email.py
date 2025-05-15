from email.message import EmailMessage
from aiosmtplib import SMTP
from ..core.config import settings


async def send_reset_email(to_email: str, token: str):
    message = EmailMessage()
    message["From"] = settings.email_username
    message["To"] = to_email
    message["Subject"] = "Reset Your Password"

    reset_link = f"http://localhost:8000/reset-password?token={token}"

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>Password Reset Request</h2>
            <p>Hello,</p>
            <p>We received a request to reset the password associated with this email address.</p>
            <p>If you made this request, please click the button below to reset your password:</p>
            <p style="text-align: center;">
                <a href="{reset_link}" style="background-color: #007BFF; color: white; padding: 10px 20px;
                   text-decoration: none; border-radius: 5px;">Reset Password</a>
            </p>
            <p><strong>Note:</strong> This link is valid for only {settings.email_expire_minutes} minutes.</p>
            <p>If you did not request a password reset, please ignore this email. Your password will remain unchanged.</p>
            <p>Thank you,<br>The Support Team</p>
        </body>
    </html>
    """

    message.set_content(
        "Please use an email client that supports HTML to view this message."
    )
    message.add_alternative(html_content, subtype="html")

    try:
        smtp = SMTP(
            hostname=settings.email_host, port=settings.email_port, start_tls=True
        )
        await smtp.connect()
        await smtp.login(settings.email_username, settings.email_password)
        await smtp.send_message(message)
        await smtp.quit()
        print("Email sent successfully!")
    except Exception as error:
        print("Error sending email:", error)
