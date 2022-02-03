from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField, RadioField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

ticket_app = ([
    ( '1', 'Server' ),
    ( '2', 'Local App' )
    ])

ticket_arg = ([
    ( '1', 'Development (code)' ),
    ( '2', 'Deploy (code)' ),
    ( '3', 'Bugs (code)' ),
    ( '4', 'ACMG criteria (variant)' ),
    ( '5', 'Bugs (front-end)' ),
    ( '6', 'Improvement Suggestion' ),
    ( '7', 'Other' )
    ])

urgency_choices = ([
    ( '1', 'Low' ),
    ( '2', 'Medium' ),
    ( '3', 'High' )
    ])

class TicketForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=250)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=1, max=4000)])
    urgency = RadioField('Urgency', choices=urgency_choices, validators=[DataRequired()] )
    application = RadioField('Application', choices=ticket_app, validators=[DataRequired()])
    argument = SelectField('Argument', choices=ticket_arg, validators=[DataRequired()])
    submit = SubmitField('Submit')

class TicketReplyForm(FlaskForm):
    body = TextAreaField('Update')
    follow = BooleanField('Follow Ticket Updates (e-mail)')
    submit = SubmitField('Update')
