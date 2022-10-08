import smtplib
import ssl
from dotenv import load_dotenv
import os
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText


class WaterEmail:

    def send_email(self, email_receiver, subject, message):
        root_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = Path(f'{root_dir}/..') / 'secret.env'
        image_path = Path(f'{root_dir}/../images/') / 'water.me.png'
        load_dotenv(dotenv_path=env_path)
        email_sender = os.environ.get('USERNAME')
        email_password = os.environ.get('PASSWORD')

        port = 465
        smtp_server = "smtp.gmail.com"
        context = ssl.create_default_context()

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = email_sender
        msg['To'] = email_receiver
        text = MIMEText(f'<h1>{message}</h1>.<br><img src="cid:image1"><br>', 'html')
        msg.attach(text)

        image = MIMEImage(open(image_path, 'rb').read())
        image.add_header('Content-ID', '<image1>')
        msg.attach(image)

        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_receiver, msg.as_string())


# x = WaterEmail()
# x.send_email(email_receiver='georgi95.bg@gmail.com', subject='Completed registration', message='Say hello to your new '
#                                                                                                'water.me account')
# x.send_email(email_receiver='danielavladimirova88@gmail.com', subject='Completed registration', message='Say hello to your new '
#                                                                                                'water.me account')



