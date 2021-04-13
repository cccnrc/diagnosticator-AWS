from flask import jsonify, current_app, request
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app.decorators import check_confirmed_API
from datetime import datetime, timedelta
from app.models import User



@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
@check_confirmed_API
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token, 'exp': basic_auth.current_user().token_expiration.strftime('%m/%d/%y %H:%M:%S:%f') })


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
@check_confirmed_API
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204


@bp.route('/check_token_exp', methods=['POST'])
@token_auth.login_required
@check_confirmed_API
def check_token_exp():
    username = token_auth.current_user().username
    user = User.query.filter_by( username = username ).first()
    return jsonify({ 'exp': user.token_expiration.strftime('%m/%d/%y %H:%M:%S:%f') })


@bp.route('/get_key', methods=['POST'])
@token_auth.login_required
@check_confirmed_API
def get_key():
    username = token_auth.current_user().username
    user = User.query.filter_by( username = username ).first()
    k = user.get_key()
    if k:
        return jsonify({ 'user_key': k })
    return jsonify({ 'error': 'too many requests' })
