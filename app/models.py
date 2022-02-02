from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from time import time
from flask import current_app
from datetime import datetime, timedelta
import base64
import os

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


import string
import random

LETTERS = string.ascii_letters
NUMBERS = string.digits
PUNCTUATION = string.punctuation


# act as auxiliary table for User and Ticket table
user_tickets = db.Table(
    "user_tickets",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("ticket_id", db.Integer, db.ForeignKey("ticket.id")),
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    institution = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    variantHG19_users = db.relationship('VariantHG19User', backref='user', foreign_keys='VariantHG19User.user_id', lazy='dynamic')
    variantHG38_users = db.relationship('VariantHG38User', backref='user', foreign_keys='VariantHG38User.user_id', lazy='dynamic')
    key = db.Column(db.String(120), unique=True)
    last_key_request = db.Column(db.DateTime)
    last_knownHG19_request = db.Column(db.DateTime)
    last_knownHG19_request_project_name = db.Column(db.String(120))
    last_knownHG38_request = db.Column(db.DateTime)
    last_knownHG38_request_project_name = db.Column(db.String(120))
    last_message_read_time = db.Column(db.DateTime)
    tickets = db.relationship('Ticket', backref='author', lazy='dynamic')
    ticket_replies = db.relationship('TicketReply', backref='replier', lazy='dynamic')
    tickets_followed = db.relationship("Ticket", secondary=user_tickets, back_populates="ticket_followers")
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_key( self ):
        if not self.key:
            printable = f'{LETTERS}{NUMBERS}{PUNCTUATION}'
            printable = list(printable)
            random.shuffle(printable)
            random_password = random.choices(printable, k=12)
            random_password = ''.join(random_password)
            self.key = generate_password_hash(random_password)

    def get_key( self ):
        if self.last_key_request:
            ### allow key release only once a hour
            if self.last_key_request > (datetime.utcnow() - timedelta(seconds=3600)):
                return None
        self.last_key_request = datetime.utcnow()
        db.session.commit()
        return self.key

    ### this is a way to create a token as a string and to put info in it
    #      the cool part is that the payload is crypted so to get the value inside "activate" you need my secret-key
    def get_jwt_token(self, expires_in=3600):
        expires_in = int(current_app.config['TOKEN_RESTORE_EXP_SEC'])
        return jwt.encode(
            {'activate': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256')

    @staticmethod
    def verify_jwt_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['activate']
        except:
            return
        return User.query.get(id)


    def get_token(self, expires_in=3600):
        expires_in = int(current_app.config['TOKEN_EXP_SEC'])
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username
        }
        return data

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient_id=self.id).filter(
            Message.timestamp > last_read_time).count()

    def new_messages_dict(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        message_list = Message.query.filter_by(recipient_id=self.id).filter(
            Message.timestamp > last_read_time).all()
        m_dict = {}
        for m in message_list:
            m_dict.update({ m.body : m.timestamp.strftime('%m/%d/%y %H:%M:%S:%f') })
        return( m_dict )




class VariantHG19User( db.Model ):
    '''
        this is the junction table to connect users and variants
    '''
    __tablename__ = 'varianthg19user'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #variant_id = db.Column(db.Integer, db.ForeignKey('varianthg19.id'))
    variant_id = db.Column(db.String(400), index=True )
    inserted_on = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    project_name = db.Column(db.String(64))
    reported_YN = db.Column(db.Boolean, default=False)
    reported = db.Column(db.String(12))
    reported_criteria = db.Column(db.String(120))
    reported_subcriteria = db.Column(db.String(120))
    reported_status = db.Column(db.String(6))
    reported_on = db.Column(db.DateTime)
    reported_num = db.Column(db.Integer, default=1)

    def __repr__(self):
        return '<Variant HG19 ID: {0} - User ID: {1}>'.format( self.variant_id, self.user_id )




class VariantHG38User( db.Model ):
    '''
        this is the junction table to connect users and variants
    '''
    __tablename__ = 'varianthg38user'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #variant_id = db.Column(db.Integer, db.ForeignKey('varianthg38.id'))
    variant_id = db.Column(db.String(400), index=True )
    inserted_on = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    project_name = db.Column(db.String(64))
    reported_YN = db.Column(db.Boolean, default=False)
    reported = db.Column(db.String(12))
    reported_criteria = db.Column(db.String(120))
    reported_subcriteria = db.Column(db.String(120))
    reported_status = db.Column(db.String(6))
    reported_on = db.Column(db.DateTime)
    reported_num = db.Column(db.Integer, default=1)

    def __repr__(self):
        return '<Variant HG38 ID: {0} - User ID: {1}>'.format( self.variant_id, self.user_id )









class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)





class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(4000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_modify = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    urgency = db.Column(db.Integer, index=True)
    application = db.Column(db.Integer, index=True)
    argument = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ticket_replies = db.relationship('TicketReply', backref='original', lazy='dynamic')
    ticket_followers = db.relationship('User', secondary=user_tickets, back_populates="tickets_followed")

    def __repr__(self):
        return '<Ticket {}>'.format(self.body)



class TicketReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(4000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    original_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))

    def __repr__(self):
        return '<Ticket Reply {}>'.format(self.body)




### ENDc
