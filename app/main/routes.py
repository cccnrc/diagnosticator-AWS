from app.main import bp
from app import db
from flask import flash
from flask import render_template, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.decorators import check_confirmed
from datetime import datetime
import os


@bp.before_request
def before_request():
    '''
        this is loaded before any request on the website
    '''
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
@bp.route('/index')
def index():
    return( render_template( 'index_DXcator.html' ) )


@bp.route('/commandVEP', methods=['GET'])
def commandVEP():
    return render_template('commandVEP_DXcator.html', title='Tutorial',
                    SERVER_ADDRESS = SERVER_ADDRESS
                    )
