import os
import smtplib
import random
import json
import datetime
from email.message import EmailMessage
from email.utils import make_msgid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
DATA_DIR = Path('data')
IMAGES_DIR = DATA_DIR / 'img'
BACKGROUNDS_DIR = DATA_DIR / 'backgrounds'
MESSAGES_FILE = DATA_DIR / 'messages_of_support.txt'
ACTIVITIES_FILE = DATA_DIR / 'selfcare_activities.txt'
RESOURCES_FILE = DATA_DIR / 'ymhc_resources.json'
REPO_RAW_URL = "https://raw.githubusercontent.com/YMHC-Charitable-Foundation/selfcare-message-emails/refs/heads/main"

# Colors
COLOR_MAIN = "#0f777c"
COLOR_BG = "#dfeeee"
COLOR_TEXT = "black"

def load_data():
    # Load Messages of Support
    with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
        messages = [line.strip() for line in f if line.strip()]
    
    # Load Self-care Activities
    with open(ACTIVITIES_FILE, 'r', encoding='utf-8') as f:
        activities = [line.strip() for line in f if line.strip()]
    
    # Load Resources
    with open(RESOURCES_FILE, 'r', encoding='utf-8') as f:
        resources = json.load(f)
        
    # Load Background Images
    backgrounds = [f.name for f in BACKGROUNDS_DIR.glob('*') if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        
    return messages, activities, resources, backgrounds

def pick_daily_content(messages, activities, resources, backgrounds):
    message = random.choice(messages)
    # Pick 4 random unique activities
    daily_activities = random.sample(activities, 4)
    # Pick 1 random resource
    resource = random.choice(resources)
    # Pick 1 random background
    background = random.choice(backgrounds) if backgrounds else None
    return message, daily_activities, resource, background

def create_email_content(message, activities, resource, background_filename):
    # IDs for inline images
    logo_cid = make_msgid(domain='ymhc.ngo')[1:-1]
    
    # Background URL logic
    # Outlook and some others don't support background-image well on non-body elements without VML.
    # We will use a robust fallback to background-color.
    # For clients that do support it, we'll strip the sophisticated gradient overlay as it's often problematic,
    # or rely on a simple image.
    
    bg_style_inline = ""
    if background_filename:
        bg_url = f"{REPO_RAW_URL}/data/backgrounds/{background_filename}"
        # We use a simple background declaration. Text shadow helps readability if image is busy.
        bg_style_inline = f"background: {COLOR_MAIN} url('{bg_url}') center center / cover no-repeat;"
    
    # Activities HTML - using Tables
    activities_html = ""
    for activity in activities:
        activities_html += f"""
        <tr>
            <td style="padding-bottom: 10px;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="{COLOR_BG}" style="border-radius: 10px; border-left: 5px solid {COLOR_MAIN};">
                    <tr>
                        <td style="padding: 15px; font-family: Helvetica, Arial, sans-serif; font-size: 16px; color: {COLOR_TEXT}; line-height: 1.4;">
                            {activity}
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        """

    # Robust HTML Email Template
    html_content = f"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Daily Message of Support</title>
<style type="text/css">
    /* Client-specific resets */
    body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ -ms-interpolation-mode: bicubic; }}
    
    /* Responsive styles */
    @media screen and (max-width: 600px) {{
        .container {{ width: 100% !important; }}
        .mobile-padding {{ padding-left: 10px !important; padding-right: 10px !important; }}
    }}
</style>
</head>
<body style="margin: 0; padding: 0; background-color: {COLOR_BG}; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
    <center>
        <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="{COLOR_BG}" style="margin: 0;">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    
                    <!-- Main Container -->
                    <table border="0" cellpadding="0" cellspacing="0" width="600" class="container" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 20px; overflow: hidden; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        
                        <!-- Header / Logo -->
                        <tr>
                            <td align="center" style="padding: 30px 20px;">
                                <img src="cid:{logo_cid}" alt="YMHC Logo" width="200" style="width: 200px; max-width: 100%; height: auto; display: block; border: 0;" />
                            </td>
                        </tr>

                        <!-- Message Block -->
                        <tr>
                            <td style="padding: 0 20px 20px 20px;" class="mobile-padding">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%" bgcolor="{COLOR_MAIN}" style="border-radius: 20px; {bg_style_inline}">
                                    <tr>
                                        <!-- Fallback color if image fails or for overlay effect -->
                                        <td align="center" valign="middle" height="300" style="padding: 40px 20px; color: #ffffff; font-family: Helvetica, Arial, sans-serif; font-size: 24px; font-weight: bold; line-height: 1.5; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                                            {message}
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Activities Section -->
                        <tr>
                            <td style="padding: 10px 20px;" class="mobile-padding">
                                <h2 style="color: {COLOR_MAIN}; font-family: Helvetica, Arial, sans-serif; font-size: 20px; text-align: center; margin-top: 10px; margin-bottom: 20px;">Today's Self-Care</h2>
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    {activities_html}
                                </table>
                            </td>
                        </tr>

                        <!-- Resource Section -->
                        <tr>
                            <td style="padding: 20px;" class="mobile-padding">
                                <h2 style="color: {COLOR_MAIN}; font-family: Helvetica, Arial, sans-serif; font-size: 20px; text-align: center; margin-top: 10px; margin-bottom: 20px;">Featured Free Resources</h2>
                                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border: 1px solid #e1e1e1; border-radius: 15px;">
                                    <tr>
                                        <td style="padding: 25px;">
                                            <h3 style="color: {COLOR_MAIN}; font-family: Helvetica, Arial, sans-serif; font-size: 18px; font-weight: bold; margin: 0 0 10px 0;">{resource['service_title']}</h3>
                                            <p style="color: #555555; font-family: Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; margin: 0 0 20px 0;">{resource['description']}</p>
                                            
                                            <!-- Bulletproof Button -->
                                            <table border="0" cellspacing="0" cellpadding="0">
                                                <tr>
                                                    <td align="center" bgcolor="{COLOR_MAIN}" style="border-radius: 25px;">
                                                        <a href="{resource['link']}" target="_blank" style="font-size: 14px; font-family: Helvetica, Arial, sans-serif; color: #ffffff; text-decoration: none; text-decoration: none; padding: 12px 25px; border-radius: 25px; border: 1px solid {COLOR_MAIN}; display: inline-block; font-weight: bold;">Learn More</a>
                                                    </td>
                                                </tr>
                                            </table>

                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Social Icons -->
                        <tr>
                            <td align="center" style="padding: 20px;">
                                <table border="0" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center" style="font-family: Helvetica, Arial, sans-serif; font-size: 12px; font-weight: bold;">
                                            <a href="https://instagram.com/youth_mental_health" style="color: {COLOR_MAIN}; text-decoration: none; margin: 0 5px;">Instagram</a> |
                                            <a href="https://tiktok.com/@youthmentalhealthaction" style="color: {COLOR_MAIN}; text-decoration: none; margin: 0 5px;">TikTok</a> |
                                            <a href="https://bsky.app/profile/ymhc.ngo" style="color: {COLOR_MAIN}; text-decoration: none; margin: 0 5px;">Bluesky</a> |
                                            <a href="https://www.facebook.com/YMHCanada" style="color: {COLOR_MAIN}; text-decoration: none; margin: 0 5px;">Facebook</a> |
                                            <a href="https://www.threads.com/@youth_mental_health" style="color: {COLOR_MAIN}; text-decoration: none; margin: 0 5px;">Threads</a> |
                                            <a href="https://www.youtube.com/channel/UC4DmXoL0nA83nFWBfZg1t-A" style="color: {COLOR_MAIN}; text-decoration: none; margin: 0 5px;">YouTube</a> |
                                            <a href="https://ymhc.substack.com/" style="color: {COLOR_MAIN}; text-decoration: none; margin: 0 5px;">Newsletters</a> |
                                            <a href="https://www.linkedin.com/company/youth-mental-health-canada/" style="color: {COLOR_MAIN}; text-decoration: none; margin: 0 5px;">LinkedIn</a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8f8f8; padding: 20px; border-top: 1px solid #cccccc;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td align="center" style="font-family: Helvetica, Arial, sans-serif; font-size: 11px; color: #888888; line-height: 1.5;">
                                            <p style="margin: 0 0 10px 0;"><strong>Safety Note:</strong> If you or someone you know is in immediate danger, please call emergency services or a crisis helpline immediately. This email is a message of support, not a substitute for professional help.</p>
                                            <p style="margin: 0 0 10px 0;">You received this message because you are subscribed to the "Daily Messages of Support" group.<br />
                                            To unsubscribe, send an email to <a href="mailto:daily-message-support+unsubscribe@ymhc.ngo" style="color: {COLOR_MAIN}; text-decoration: underline;">daily-message-support+unsubscribe@ymhc.ngo</a>.</p>
                                            <p style="margin: 0;">YMHC is a registered charity. BN: 771374915RR0001. <a href="https://www.canadahelps.org/en/charities/ymhc-charitable-foundation/" style="color: {COLOR_MAIN}; text-decoration: underline;">Make a donation</a>.</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                    </table>
                    <!-- End Main Container -->
                    
                </td>
            </tr>
        </table>
    </center>
</body>
</html>
    """
    return html_content, logo_cid

def send_email():
    # Load data
    messages, activities, resources, backgrounds = load_data()
    msg_text, daily_acts, resource, background_filename = pick_daily_content(messages, activities, resources, backgrounds)
    
    # Create HTML
    html_content, logo_cid = create_email_content(msg_text, daily_acts, resource, background_filename)

    # Save local preview (for debugging/verification)
    preview_html = html_content.replace(f'cid:{logo_cid}', 'data/img/logo-transparent.png')
    with open('preview.html', 'w', encoding='utf-8') as f:
        f.write(preview_html)
    print("Generated preview.html")
    
    # Email Setup
    sender_email = os.environ.get('EMAIL_USER')
    recipient_email = os.environ.get('RECIPIENT_EMAIL')
    smtp_server = os.environ.get('EMAIL_HOST')
    smtp_port = int(os.environ.get('EMAIL_PORT') or 587)
    smtp_password = os.environ.get('EMAIL_PASSWORD')

    missing_vars = []
    if not sender_email: missing_vars.append('EMAIL_USER')
    if not recipient_email: missing_vars.append('RECIPIENT_EMAIL')
    if not smtp_server: missing_vars.append('EMAIL_HOST')
    if not smtp_password: missing_vars.append('EMAIL_PASSWORD')

    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your GitHub Secrets (or .env file locally).")
        exit(1)

    msg = MIMEMultipart('related')
    msg['Subject'] = f"Daily Message of Support - {datetime.date.today().strftime('%B %d, %Y')}"
    msg['From'] = f"Youth Mental Health Canada <{sender_email}>"
    msg['To'] = recipient_email

    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)

    # Plain text fallback
    plain_text = f"""
"{msg_text}"

Today's Self-Care Activities:
{chr(10).join(['- ' + act for act in daily_acts])}

Featured Resource:
{resource['service_title']}
{resource['link']}

(Please enable HTML to view the full beautiful email!)
    """
    msg_alternative.attach(MIMEText(plain_text, 'plain'))
    msg_alternative.attach(MIMEText(html_content, 'html'))

    # Attach Images
    # Logo
    try:
        with open(IMAGES_DIR / 'logo-transparent.png', 'rb') as img:
            mime_logo = MIMEImage(img.read())
            mime_logo.add_header('Content-ID', f'<{logo_cid}>')
            mime_logo.add_header('Content-Disposition', 'inline')
            msg.attach(mime_logo)
    except FileNotFoundError:
        print("Warning: Logo image not found.")

    # Send
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, smtp_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email()
