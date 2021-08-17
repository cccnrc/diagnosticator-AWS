from app import db
from app.auth import bp
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

import requests


from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password( username, password ):
    user = User.query.filter_by( username = username ).first()
    if user:
        if user.check_password( password ):
            return( True )
    return( False )






### page WITHOUT authentication need
@bp.route('/unauthenticate', methods=['GET', 'POST'])
def unauthenticate():
    return("Hello UN-authenticated user!")


### page WITH authentication need
@bp.route('/authenticate_basic', methods=['GET', 'POST'])
@auth.login_required
def authenticate_basic():
    return "Hello, {}!".format(auth.current_user())




@bp.route('/generate_token/<username>', methods=['GET', 'POST'])
def generate_token( username ):
    user = User.query.filter_by( username = username ).first()
    token = user.get_token()
    text = "Hello: {0}, your token: {1}".format( username, token )
    return( text )


@bp.route('/authenticate_token/<token>', methods=['GET', 'POST'])
def authenticate_token( token ):
    user = User.verify_post_token(token)
    if not user:
        return( "Unvalid token" )
    return( "Hello {}!".format(user.username) )











############ SERVER PAGES
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.auth.email import send_password_reset_email, send_activation_email
from app.decorators import check_confirmed





@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

import re
def password_validation( password ):
    '''
        this is to be sure that the pwd is a strong password:
        - at least 8 chars
        - at least a capital letter
        - at least a number
        - at least a special characters
    '''
    if len(password) < 8:
        flash("Make sure your password is at lest 8 characters", 'danger')
        return( False )
    if re.search('[0-9]',password) is None:
        flash("Make sure your password has a number in it", 'danger')
        return( False )
    if re.search('[A-Z]',password) is None:
        flash("Make sure your password has a capital letter in it", 'danger')
        return( False )
    special_character = '[!@#$%^&*(),.?":{}|<>+-=]'
    if not len(set(special_character).intersection(set( password ))) > 0:
        flash("Make sure your password has a special character in it", 'danger')
        return( False )
    return( True )

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        pwd = form.password.data
        if not password_validation(pwd) :
            return redirect(url_for('auth.register'))
        user = User( username=form.username.data, email=form.email.data, institution=form.institution.data, confirmed=False )
        user.set_password(pwd)
        user.set_key()
        db.session.add(user)
        db.session.commit()
        ### confirmation mail
        send_activation_email(user)
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register',
                           form=form)


@bp.route('/login', methods=['GET', 'POST'])
@check_confirmed
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_jwt_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/confirm/<token>')
#@login_required
def confirm_email(token):
    user = User.verify_jwt_token(token)
    if not user:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.unconfirmed'))
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('main.index'))


@bp.route('/unconfirmed')
# @login_required
def unconfirmed():
    if current_user.is_anonymous:
        flash('Please confirm your account!', 'warning')
    else:
        if current_user.confirmed:
            return redirect(url_for('main.index'))
    flash('Please confirm your account!', 'warning')
    return render_template('auth/unconfirmed_DXcator.html')


@bp.route('/resend')
@login_required
def resend_confirmation():
    send_activation_email( current_user )
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('auth.unconfirmed'))
