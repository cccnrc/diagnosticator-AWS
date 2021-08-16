from flask import render_template, current_app
from app.email import send_email

def send_password_reset_email(user):
    token = user.get_jwt_token()
    send_email('[Diagnosticator] Reset Your Password',
               # sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_activation_email(user):
    token = user.get_jwt_token()
    send_email('[Diagnosticator] Confirm Your Mail',
               # sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/activate.txt',
                                         user=user, token=token),
               html_body=render_template('email/activate.html',
                                         user=user, token=token))
