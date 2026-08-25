import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from app.interfaces.channel_sender_interface import IChannelSender

class EmailSender(IChannelSender):
    def __init__(self):
        self.smtp_host = os.environ["SMTP_HOST"]
        self.smtp_port = int(os.environ["SMTP_PORT"])
        self.smtp_user = os.environ["SMTP_USER"]
        self.smtp_password = os.environ["SMTP_PASSWORD"]

    def send(self, destinataire: str, message: str) -> dict:
        try:
            mail = MIMEMultipart()
            mail["From"] = self.smtp_user
            mail["To"] = destinataire
            mail["Subject"] = "Une opportunité pour votre entreprise"
            mail.attach(MIMEText(message, "plain"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(mail)
            return {"statut": "envoye"}

        except smtplib.SMTPRecipientsRefused:
            return {"statut": "echec", "raison": "adresse refusée"}
        except smtplib.SMTPException as e:
            return {"statut": "echec", "raison": str(e)}