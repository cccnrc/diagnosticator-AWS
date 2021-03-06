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

def send_ticket_closure_email(user, ticket):
    send_email('[Diagnosticator] Ticket Closure',
               # sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               subject = 'Diagnosticator - Ticket Closure',
               text_body=render_template('email/ticket_closure.txt',
                                         user=user, ticket = ticket),
               html_body=render_template('email/ticket_closure.html',
                                         user=user, ticket = ticket))

def send_ticket_reopen_email(user, ticket):
    send_email('[Diagnosticator] Ticket Reopen',
               recipients=[user.email],
               subject = 'Diagnosticator - Ticket Reopen',
               text_body=render_template('email/ticket_reopen.txt',
                                         user=user, ticket = ticket),
               html_body=render_template('email/ticket_reopen.html',
                                         user=user, ticket = ticket))
