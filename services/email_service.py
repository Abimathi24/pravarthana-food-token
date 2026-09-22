import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from config import Config
import io
import base64

class EmailService:
    @staticmethod
    def send_qr_email(to_email, student_name, qr_base64_str, token_id):
        # In a real production scenario, use async queues like Celery, 
        # or services like SendGrid/Mailgun. 
        # Here we use smtplib as requested for a standalone Flask app.
        
        if not Config.MAIL_SERVER or not Config.MAIL_USERNAME:
            print("Email settings not configured.")
            return False

        try:
            msg = MIMEMultipart('related')
            msg['Subject'] = "PRAVARTHANA 2026 - Your Food Token"
            msg['From'] = Config.MAIL_FROM
            msg['To'] = to_email

            html = f"""
            <html>
                <body>
                    <h2>Hello {student_name},</h2>
                    <p>Here is your food token for PRAVARTHANA 2026.</p>
                    <p><strong>Token ID:</strong> {token_id}</p>
                    <p>Please show this QR code at the food counter.</p>
                    <img src="cid:qrcode" alt="QR Code" style="width:200px; height:200px;">
                    <br>
                    <p>Thank you!</p>
                </body>
            </html>
            """
            
            part1 = MIMEText(html, 'html')
            msg.attach(part1)

            # Decode base64 QR to bytes
            qr_bytes = base64.b64decode(qr_base64_str.split(',')[1])
            img = MIMEImage(qr_bytes)
            img.add_header('Content-ID', '<qrcode>')
            msg.attach(img)

            server = smtplib.SMTP(Config.MAIL_SERVER, int(Config.MAIL_PORT))
            server.starttls()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
