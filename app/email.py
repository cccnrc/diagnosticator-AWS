from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail
import boto3

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(app, recipients, sender=None, subject='', text_body='', html_body='',
                attachments=None, sync=False):
    ses = boto3.client(
        'ses',
        region_name = current_app.config['SES_REGION_NAME'],
        aws_access_key_id = current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key = current_app.config['AWS_SECRET_ACCESS_KEY'],
        aws_session_token = current_app.config['AWS_SESSION_TOKEN']
    )
    if not sender:
        sender = current_app.config['SES_EMAIL_SOURCE']
    ses.send_email(
        Source=sender,
        Destination={ 'ToAddresses': recipients },
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Text': {'Data': text},
                'Html': {'Data': html}
            }
        }
    )


'''
### OLD mail sender with flask_mail
def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email,
            args=(current_app._get_current_object(), msg)).start()
'''
