from app import mail
from flask_mail import Message
from flask import current_app
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, text_body, html_body, recipients, attachments=None, sync=False):
    msg = Message(subject=subject, sender=sender, recipients=recipients, body=text_body, html=html_body)
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)

    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email, args=(current_app.get_current_object(), msg)).start()