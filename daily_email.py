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
    
    # Background URL
    if background_filename:
        bg_url = f"{REPO_RAW_URL}/data/backgrounds/{background_filename}"
        # Linear gradient overlay + image
        bg_style = f"background-image: linear-gradient(rgba(15, 119, 124, 0.7), rgba(15, 119, 124, 0.7)), url('{bg_url}');"
    else:
        # Fallback if no images found
        bg_style = ""
    
    # Activities HTML
    activities_html = ""
    for activity in activities:
        activities_html += f"""
        <div style="background-color: white; border-radius: 10px; padding: 15px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid {COLOR_MAIN};">
            <p style="margin: 0; font-size: 16px; color: {COLOR_TEXT};">{activity}</p>
        </div>
        """

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body {{ margin: 0; padding: 0; background-color: {COLOR_BG}; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }}
    .container {{ max-width: 600px; margin: 0 auto; background-color: {COLOR_BG}; padding: 20px; }}
    .card {{ background-color: white; border-radius: 20px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .header {{ text-align: center; padding: 20px 0; }}
    .logo {{ max-width: 200px; height: auto; }}
    
    /* Block A: Message of Support */
    .message-block {{ 
        background-color: {COLOR_MAIN}; 
        color: white; 
        text-align: center; 
        padding: 40px 20px; 
        border-radius: 20px; 
        margin-bottom: 20px;
        position: relative;
        {bg_style}
        background-size: cover;
        background-position: center;
    }}
    .message-text {{ 
        position: relative; 
        z-index: 2; 
        font-size: 24px; 
        font-weight: bold; 
        line-height: 1.4; 
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    .section-title {{ color: {COLOR_MAIN}; text-align: center; margin-bottom: 15px; font-size: 20px; font-weight: bold; }}
    
    /* Block C: Resource */
    .resource-card {{ background-color: white; border-radius: 15px; padding: 20px; border: 1px solid #e1e1e1; text-align: left; }}
    .resource-title {{ color: {COLOR_MAIN}; font-size: 18px; font-weight: bold; margin-top: 0; margin-bottom: 10px; }}
    .resource-desc {{ color: #555; font-size: 14px; line-height: 1.5; margin-bottom: 15px; }}
    .resource-btn {{ display: inline-block; background-color: {COLOR_MAIN}; color: white !important; text-decoration: none; padding: 10px 20px; border-radius: 25px; font-size: 14px; font-weight: bold; }}
    
    /* Footer & Social */
    .social-icons {{ text-align: center; margin: 30px 0 20px 0; }}
    .social-link {{ text-decoration: none; margin: 0 5px; color: {COLOR_MAIN} !important; font-size: 12px; font-weight: bold; }}
    .footer {{ text-align: center; font-size: 11px; color: #888; line-height: 1.5; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ccc; }}
    
    @media only screen and (max-width: 480px) {{
        .container {{ padding: 10px; }}
        .message-text {{ font-size: 20px; }}
    }}
</style>
</head>
<body>
    <div class="container">
        <!-- Logo -->
        <div class="header">
            <img src="cid:{logo_cid}" alt="YMHC Logo" class="logo">
        </div>

        <!-- Block A: Daily Message -->
        <div class="message-block">
            <div class="section-title">Daily Message of Support</div>
            <div class="message-text">“{message}”</div>
        </div>

        <!-- Block B: Self-care Activities -->
        <div class="section-title">Today's Self-Care</div>
        {activities_html}

        <!-- Block C: Resource -->
        <div class="section-title" style="margin-top: 30px;">Featured Resource</div>
        <div class="resource-card">
            <h3 class="resource-title">{resource['service_title']}</h3>
            <p class="resource-desc">{resource['description']}</p>
            <a href="{resource['link']}" class="resource-btn">Learn More</a>
        </div>

        <!-- Social Icons -->
        <div class="social-icons">
            <a href="https://instagram.com/youth_mental_health" class="social-link">Instagram</a> | 
            <a href="https://tiktok.com/@youthmentalhealthaction" class="social-link">TikTok</a> | 
            <a href="https://www.facebook.com/YMHCanada" class="social-link">Facebook</a> | 
            <a href="https://www.threads.com/@youth_mental_health" class="social-link">Threads</a> | 
            <a href="https://www.youtube.com/channel/UC4DmXoL0nA83nFWBfZg1t-A" class="social-link">YouTube</a> | 
            <a href="https://ymhc.substack.com/" class="social-link">Monthly Newsletters</a> | 
            <a href="https://www.linkedin.com/company/youth-mental-health-canada/" class="social-link">LinkedIn</a>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><strong>Safety Note:</strong> If you or someone you know is in immediate danger, please call emergency services or a crisis helpline immediately. This email is a message of support, not a substitute for professional help.</p>
            <p>You received this message because you are subscribed to the Google Groups "Daily Messages of Support" group.<br>
            To unsubscribe from this group and stop receiving emails from it, send an email to <a href="mailto:daily-message-support+unsubscribe@ymhc.ngo" style="color: {COLOR_MAIN}">daily-message-support+unsubscribe@ymhc.ngo</a>.</p>
        </div>
    </div>
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
Daily Message of Support

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
