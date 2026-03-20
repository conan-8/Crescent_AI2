import os
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

def send_daily_report():
    # Load environment variables
    load_dotenv()
    
    # Email configuration
    # Please add these to your .env file
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD") # Suggest using an App Password for Gmail
    recipient_email = os.environ.get("RECIPIENT_EMAIL") 
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 465))
    
    if not all([sender_email, sender_password, recipient_email]):
        print("Error: Missing email configuration.")
        print("Please ensure SENDER_EMAIL, SENDER_PASSWORD, and RECIPIENT_EMAIL are set in your .env file.")
        return

    # Construct the path to today's report
    current_date_str = datetime.datetime.now().strftime("%Y_%m_%d")
    report_filename = f"{current_date_str}_analysis_report.md"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(script_dir, "analysis_reports", report_filename)
    
    if not os.path.exists(report_path):
        print(f"Error: The report for today '{report_filename}' was not found in 'analysis_reports'.")
        print("Please make sure the analysis_agent.py script has run today before running this script.")
        return
        
    print(f"Found today's report: {report_filename}")
    print(f"Preparing to send email to: {recipient_email}...")

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"Daily Analysis Report - {datetime.datetime.now().strftime('%B %d, %Y')}"
    
    body = "Attached is the newly generated daily analysis report for the chatbot."
    msg.attach(MIMEText(body, 'plain'))

    # Attach the file
    try:
        with open(report_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={report_filename}',
        )
        msg.attach(part)
    except Exception as e:
        print(f"Failed to read or attach the file: {e}")
        return

    # Send the email
    try:
        # Set up the SMTP server
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        # Login
        server.login(sender_email, sender_password)
        # Send mail
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error details:\n{e}")

if __name__ == "__main__":
    send_daily_report()
