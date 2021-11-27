"""
Mail services
"""
from app import *
from flask_mail import Message
from threading import Thread

def send_email(app,msg):
    with app.app_context():
        mail.send(msg)


def email(recipients,text_body,html_body):
    msg = Message()
    msg.subject = '[User] Password reset'
    msg.recipients = recipients
    msg.sender = app.config['MAIL_USERNAME']
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_email, args=(app,msg))
    #mail.send(msg)
    send_email(app,msg)
    return 'sent'




