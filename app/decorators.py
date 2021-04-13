from functools import wraps

from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from app import db
from app.models import User
from app.api.errors import error_response, unconfirmed
from app.api.auth import basic_auth, token_auth

def check_confirmed(func):
    '''
        this is to check that author has confirmed their mail
    '''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_anonymous:
            if current_user.confirmed is False:
                return redirect(url_for('auth.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function



def check_confirmed_API( func ):
    '''
        this is able to check that the API authenticating author has confirmed their mail
    '''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if basic_auth.current_user():
            username = basic_auth.current_user().username
        elif token_auth.current_user() :
            username = token_auth.current_user().username
        user = User.query.filter_by( username = username ).first()
        if not user:
            return( error_response(401) )
        if user.confirmed is False:
            return( unconfirmed() )
        return func(*args, **kwargs)

    return decorated_function




def check_variant_SQL_DB( func ):
    '''
        this is able to check that the app is running variant DB in SQL environment
    '''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_app.config['VARIANT_DB'] != 'SQL':
            print( "This server is not running Variant DB in SQL, VARIANT_DB: {}".format(current_app.config['VARIANT_DB']) )
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)

    return decorated_function
