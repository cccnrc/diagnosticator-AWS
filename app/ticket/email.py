from flask import render_template, current_app
from app.email import send_email

def send_ticket_email(user, ticket):
    send_email('[Diagnosticator] Ticket Update',
               # sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               subject = 'Diagnosticator - Ticket Update',
               text_body=render_template('email/ticket.txt',
                                         user=user, ticket = ticket),
               html_body=render_template('email/ticket.html',
                                         user=user, ticket = ticket))
