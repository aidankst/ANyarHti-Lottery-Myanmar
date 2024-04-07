import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

def send_email(subject, to_email, lottery_ticket):
    gmail_user = ''
    gmail_password = '' 

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = to_email

    html_body = """
    <html>
        <body>
            <p>Hello,</p>
            <p>Thank you for your purchase! Here is your ticket.</p>
            <p>Best regards,<br>အညာထီ</p>
        </body>
    </html>
    """

    part = MIMEText(html_body, 'html')
    msg.attach(part)

    with open(lottery_ticket, "rb") as attachment:
        img = MIMEImage(attachment.read())
        img.add_header('Content-Disposition', 'attachment', filename=lottery_ticket)
        msg.attach(img)


    server = smtplib.SMTP('smtp.gmail.com', 587)  
    server.starttls() 
    server.login(gmail_user, gmail_password)
    server.send_message(msg)
    server.quit()