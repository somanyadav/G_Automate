import smtplib
import pandas as pd
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import json

def create_email_body(df_shortlisted):
    """Create a beautiful HTML email body with job listings"""
    
    if df_shortlisted.empty:
        return """
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <h2 style="color: #2c3e50;">🔍 Weekly Job Analysis Report</h2>
            <p>No jobs met your criteria this week. The system will keep looking for you!</p>
            <p style="color: #7f8c8d; font-size: 12px;">Generated on {date}</p>
        </body>
        </html>
        """.format(date=datetime.now().strftime("%B %d, %Y at %I:%M %p"))
    
    # Sort by fit score descending
    df_sorted = df_shortlisted.sort_values('fit_score', ascending=False)
    
    # Create HTML table
    table_rows = ""
    for _, job in df_sorted.iterrows():
        # Handle potential missing data
        title = job.get('job_title', 'N/A')
        score = job.get('fit_score', 'N/A')
        category = job.get('fit_category', 'N/A')
        url = job.get('job_url', '#')
        location = job.get('location', 'N/A')
        experience_level = job.get('experience_level', 'N/A')
        key_matches = job.get('key_matches', [])
        outreach_snippet = job.get('auto_drafted_outreach_snippet', 'N/A')
        
        # Format key matches
        if isinstance(key_matches, list):
            matches_text = ', '.join(key_matches[:3])  # Show first 3 matches
            if len(key_matches) > 3:
                matches_text += f" (+{len(key_matches)-3} more)"
        else:
            matches_text = str(key_matches) if key_matches else 'N/A'
        
        # Color code based on score
        if isinstance(score, (int, float)):
            if score >= 9:
                score_color = "#27ae60"  # Green
            elif score >= 8:
                score_color = "#f39c12"  # Orange
            else:
                score_color = "#3498db"  # Blue
        else:
            score_color = "#95a5a6"  # Gray
        
        table_rows += f"""
        <tr style="border-bottom: 1px solid #ecf0f1;">
            <td style="padding: 15px; vertical-align: top;">
                <div style="font-weight: bold; font-size: 16px; color: #2c3e50; margin-bottom: 5px;">
                    <a href="{url}" style="color: #3498db; text-decoration: none;" target="_blank">
                        {title}
                    </a>
                </div>
                <div style="color: #7f8c8d; font-size: 14px; margin-bottom: 5px;">
                    📍 {location} | 👔 {experience_level}
                </div>
                <div style="color: #2c3e50; font-size: 13px; margin-bottom: 8px;">
                    <strong>Key Matches:</strong> {matches_text}
                </div>
                <div style="background: #f8f9fa; padding: 8px; border-radius: 4px; font-size: 12px; color: #2c3e50; font-style: italic;">
                    💬 {outreach_snippet[:150]}{'...' if len(str(outreach_snippet)) > 150 else ''}
                </div>
            </td>
            <td style="padding: 15px; text-align: center; vertical-align: top;">
                <div style="background: {score_color}; color: white; padding: 8px 12px; border-radius: 20px; font-weight: bold; font-size: 14px; margin-bottom: 5px;">
                    {score}/10
                </div>
                <div style="font-size: 12px; color: #7f8c8d;">
                    {category}
                </div>
            </td>
            <td style="padding: 15px; text-align: center; vertical-align: top;">
                <a href="{url}" target="_blank" style="background: #3498db; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; font-size: 14px; font-weight: bold;">
                    Apply Now
                </a>
            </td>
        </tr>
        """
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
            .content {{ padding: 20px; }}
            .stats {{ background: #ecf0f1; padding: 15px; border-radius: 6px; margin: 15px 0; }}
            .job-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .footer {{ background: #34495e; color: white; padding: 15px; border-radius: 0 0 8px 8px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0; font-size: 24px;">🎯 Your Weekly Job Matches</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
            </div>
            
            <div class="content">
                <div class="stats">
                    <h3 style="margin: 0 0 10px 0; color: #2c3e50;">📊 This Week's Summary</h3>
                    <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                        <div><strong>{len(df_sorted)}</strong> jobs matched your criteria</div>
                        <div><strong>{len(df_sorted[df_sorted['fit_score'] >= 9])}</strong> excellent matches (9+ score)</div>
                        <div><strong>{len(df_sorted[df_sorted['fit_score'] >= 8])}</strong> great matches (8+ score)</div>
                    </div>
                </div>
                
                <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">🚀 Your Shortlisted Opportunities</h3>
                
                <table class="job-table">
                    <thead>
                        <tr style="background: #34495e; color: white;">
                            <th style="padding: 12px; text-align: left; width: 60%;">Job Details</th>
                            <th style="padding: 12px; text-align: center; width: 20%;">Fit Score</th>
                            <th style="padding: 12px; text-align: center; width: 20%;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                
                <div style="margin-top: 20px; padding: 15px; background: #e8f6ff; border-left: 4px solid #3498db; border-radius: 4px;">
                    <h4 style="margin: 0 0 10px 0; color: #2c3e50;">💡 Pro Tips for This Week</h4>
                    <ul style="margin: 0; color: #2c3e50;">
                        <li>Focus on jobs with 8+ scores for highest success rate</li>
                        <li>Use the outreach snippets for LinkedIn networking</li>
                        <li>Check the attached CSV for complete details and contact info</li>
                        <li>Set up Google Alerts for companies you're interested in</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p style="margin: 0;">🤖 Automated by your GitHub Actions job analysis system</p>
                <p style="margin: 5px 0 0 0; opacity: 0.8;">Next analysis: {(datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + pd.Timedelta(days=7)).strftime("%B %d, %Y")}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_body

def send_job_email():
    """Send email with shortlisted jobs"""
    
    # Email configuration from environment variables
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_APP_PASSWORD')  # Gmail App Password
    recipient_email = os.getenv('RECIPIENT_EMAIL', sender_email)  # Default to sender if not specified
    
    if not sender_email or not sender_password:
        print("❌ Email credentials not found in environment variables")
        print("Required: SENDER_EMAIL, SENDER_APP_PASSWORD")
        return False
    
    # Check if shortlisted file exists
    shortlisted_file = "shortlisted_google_jobs_full.csv"
    if not os.path.exists(shortlisted_file):
        print(f"❌ Shortlisted jobs file not found: {shortlisted_file}")
        return False
    
    # Load shortlisted jobs
    try:
        df_shortlisted = pd.read_csv(shortlisted_file)
        print(f"📊 Found {len(df_shortlisted)} shortlisted jobs")
    except Exception as e:
        print(f"❌ Error reading shortlisted jobs file: {e}")
        return False
    
    # Create email
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"🎯 {len(df_shortlisted)} New Job Matches - Week of {datetime.now().strftime('%b %d, %Y')}"
    
    # Create HTML body
    html_body = create_email_body(df_shortlisted)
    html_part = MIMEText(html_body, 'html')
    msg.attach(html_part)
    
    # Attach CSV file
    try:
        with open(shortlisted_file, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {shortlisted_file}'
            )
            msg.attach(part)
        print("✅ CSV file attached successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not attach CSV file: {e}")
    
    # Send email using Gmail SMTP
    try:
        print("📤 Sending email...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"✅ Email sent successfully to {recipient_email}")
        print(f"📋 Subject: {msg['Subject']}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    success = send_job_email()
    if success:
        print("\n🎉 Job notification email sent successfully!")
    else:
        print("\n💥 Email sending failed. Check logs above for details.")
