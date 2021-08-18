from app.main import bp
from app import db
from flask import flash
from flask import render_template, current_app, send_from_directory
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

########################################################
################      DOCUMENTATION      ###############
########################################################
@bp.route('/commandVEP', methods=['GET'])
@login_required
def commandVEP():
    return render_template('commandVEP_DXcator.html', title='VEP command')

@bp.route('/filtering', methods=['GET'])
@login_required
def filtering():
    return render_template('filtering_DXcator.html', title='Filtering')

@bp.route('/multiple_projects', methods=['GET'])
@login_required
def multiple_projects():
    return render_template('multiple_projects_DXcator.html', title='More')

@bp.route('/installation', methods=['GET'])
@login_required
def installation():
    return render_template('installation_DXcator.html', title='Install')

@bp.route('/development_installation', methods=['GET'])
@login_required
def development_installation():
    return render_template('development_installation_DXcator.html', title='Development')

@bp.route('/development_installation_docker', methods=['GET'])
@login_required
def development_installation_docker():
    return render_template('development_installation_docker_DXcator.html', title='Docker')

@bp.route('/development_installation_flask', methods=['GET'])
@login_required
def development_installation_flask():
    return render_template('development_installation_flask_DXcator.html', title='Flask')

@bp.route('/download/<path:filename>')
@login_required
def download( filename ):
    return send_from_directory( 'static', filename, as_attachment=True )

@bp.route('/documentation')
def documentation():
    return render_template('documentation.html', title='Doc')
