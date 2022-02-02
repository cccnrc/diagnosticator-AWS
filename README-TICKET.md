# Diagnosticator Ticket

This is to setup the ticketing system in Diagnosticator

## New branch

1. create structure
```
APP_DIR=$( pwd )
mkdir ${APP_DIR}/app/ticket
mkdir ${APP_DIR}/app/templates/ticket/                ### for templates
atom ${APP_DIR}/app/ticket/__init__.py                ### specify the INIT
```

2. add this to `app/__init__.py`:
```
from app.ticket import bp as ticket_bp
app.register_blueprint( ticket_bp, url_prefix='/ticket' )
```


3. create a `app/ticket/routes.py` function and an HTML page:
```
atom ${APP_DIR}/app/ticket/routes.py                  ### create some routes
atom ${APP_DIR}/app/ticket/forms.py                   ### create some forms
atom ${APP_DIR}/app/templates/ticket/index.html     ### create a template
```

4. specify `ticket.bp` in `app/ticket/routes.py`:
```
from app.ticket import bp
```

5. inside `app/ticket/routes.py` functions, point templates to `app/templates/ticket/` directory:
```
return( render_template( 'ticket/index.html' ))
```

6. add `Ticket` class inside `app/models.py`:
```
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(400))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Ticket {}>'.format(self.body)
```

7. add relationship with `User` table in `app/models.py`:
```
### within User class
tickets = db.relationship('Ticket', backref='author', lazy='dynamic')
```

8. update databse:
```
flask db migrate -m "tickets table"
flask db upgrade
```

9. if you need to send mail in this branch, create a `app/ticket/email.py` and define a function. Example:
```
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
```

10. create `app/templates/email/ticket.txt` and `app/templates/email/ticket.html`

11. import email functions into `app/ticket/routes.py` and use it:
```
from app.ticket.email import send_ticket_email

# ... #
for single_user in ticket.ticket_followers:
          send_ticket_email(single_user, ticket_reply)
# ... #
```
