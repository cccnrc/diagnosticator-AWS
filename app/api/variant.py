from flask import jsonify, request, url_for, abort
from app import db
from app.models import User, Message
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
import json

from flask import request
import requests
from datetime import datetime

@bp.route('/post_data', methods=['POST'])
@token_auth.login_required
def post_data():
    '''
        this is to check that the local machine can POST data to server
        - LOCAL: auth.development_check_send_data_to_server()
    '''
    input_json = request.get_json( force=True )
    username = token_auth.current_user().username
    if input_json['date_client'] == datetime.utcnow().strftime("%m-%d-%Y"):
        dictToReturn = ({ 'date_server' : datetime.utcnow().strftime("%m-%d-%Y"), 'username' : username })
    else:
        dictToReturn = {}
    return(jsonify(dictToReturn))



@bp.route('/get_username', methods=['GET'])
@token_auth.login_required
def get_variant():
    '''
        this is to check that the local machine can GET data from server
        - LOCAL: auth.development_check_get_data_from_server()
    '''
    username = token_auth.current_user().username
    dictToReturn = ({ 'username' : username })
    return(jsonify(dictToReturn))


from flask import current_app
from app.decorators import check_variant_SQL_DB
from app.models import VariantHG19User, VariantHG38User

@bp.route('/post_variants', methods=['POST'])
@token_auth.login_required
def post_variants():
    '''
        this is to store vairants received from users
    '''
    input_json = request.get_json( force=True )
    username = token_auth.current_user().username
    if 'variants_dict' in input_json and 'assembly' in input_json:
        variants_dict = input_json['variants_dict']
        if update_variant_user_SQL( username, variants_dict['var_list'], input_json['assembly'], input_json['project_name'] ):
            dictToReturn = ({ 'vars_added' : len(variants_dict['var_list']) })
    else:
        dictToReturn = {}
    return(jsonify(dictToReturn))





@bp.route('/report_variant', methods=['POST'])
@token_auth.login_required
def report_variant():
    '''
        this is to store vairants received from users (ACCEPTED)
    '''
    input_json = request.get_json( force=True )
    username = token_auth.current_user().username
    user = User.query.filter_by( username = username ).first()
    dictToReturn = ({ 'var_added' : 'NONE' })
    if 'var_accepted' in input_json and 'var_accepted_ACMG' in input_json and 'assembly' in input_json:
        ### if reported from same user with same ACMG overall classification just add +1 to that report
        if input_json['assembly'] == 'hg19':
            try:
                variant = VariantHG19User.query.filter_by(
                                                        user_id = user.id,
                                                        variant_id = input_json['var_accepted'],
                                                        reported_criteria = input_json['var_accepted_ACMG'],
                                                    ).first()
                variant.last_seen = datetime.utcnow()
                variant.reported_num += 1
                db.session.commit()
                dictToReturn = ({ 'var_added' : input_json['var_accepted'], 'report_num': variant.reported_num })
            except:
                variant = VariantHG19User(
                    user_id = user.id,
                    variant_id = input_json['var_accepted'],
                    reported_criteria = input_json['var_accepted_ACMG'],
                    reported_subcriteria = input_json['var_accepted_ACMG_criterias'],
                    reported_status = input_json['var_accepted_status'],
                    project_name = input_json['project_name'],
                    reported_YN = True
                )
                db.session.add( variant )
                db.session.commit()
                dictToReturn = ({ 'var_added' : input_json['var_accepted'], 'report_num': 1 })
        elif input_json['assembly'] == 'hg38':
            try:
                variant = VariantHG38User.query.filter_by(
                                                        user_id = user.id,
                                                        variant_id = input_json['var_accepted'],
                                                        reported_criteria = input_json['var_accepted_ACMG'],
                                                    ).first()
                variant.last_seen = datetime.utcnow()
                variant.reported_num += 1
                db.session.commit()
                dictToReturn = ({ 'var_added' : input_json['var_accepted'], 'report_num': variant.reported_num })
            except:
                variant = VariantHG38User(
                    user_id = user.id,
                    variant_id = input_json['var_accepted'],
                    reported_criteria = input_json['var_accepted_ACMG'],
                    reported_subcriteria = input_json['var_accepted_ACMG_criterias'],
                    reported_status = input_json['var_accepted_status'],
                    project_name = input_json['project_name'],
                    reported_YN = True
                )
                db.session.add( variant )
                db.session.commit()
                dictToReturn = ({ 'var_added' : input_json['var_accepted'], 'report_num': 1 })
    return(jsonify(dictToReturn))







@bp.route('/get_user_new_messages', methods=['POST'])
@token_auth.login_required
def get_user_new_messages():
    '''
        this is for the users to ask for notifications regarding their variants
    '''
    # input_json = request.get_json( force=True )
    new_messages_N = token_auth.current_user().new_messages()
    last_message_read_time = token_auth.current_user().last_message_read_time or datetime(1900, 1, 1)
    dictToReturn = ({
            'new_messages_N' : new_messages_N,
            'prev_read_time' : last_message_read_time.strftime('%m/%d/%y %H:%M:%S:%f'),
            'm_dict' : token_auth.current_user().new_messages_dict()
    })
    # token_auth.current_user().last_message_read_time = datetime.utcnow()
    return(jsonify( dictToReturn ))




@bp.route('/post_var', methods=['POST'])
@token_auth.login_required
def post_var():
    '''
        this is to store single accepted variants
    '''
    report_statuses = [ 'LP', 'P', 'B' ]
    input_json = request.get_json( force=True )
    username = token_auth.current_user().username
    if 'var_accepted' in input_json and 'var_accepted_ACMG' in input_json and 'var_accepted_status' in input_json and 'project_name' in input_json and 'assembly' in input_json:
        var_user = get_var_user( input_json['var_accepted'], username, input_json['assembly'], input_json['project_name'] )
        try:
            var_user.reported = input_json['var_accepted_ACMG']['ACMG']
            input_json['var_accepted_ACMG'].pop('ACMG', None)
            var_user.reported_criteria = json.dumps(input_json['var_accepted_ACMG'])
        except:
            var_user.reported = 'NA'
            var_user.reported_criteria = json.dumps('NA')
        ### notify other users
        if var_user.reported in report_statuses:
            u_dict = get_var_users( input_json['var_accepted'], input_json['assembly'] )
            u_dict.pop( token_auth.current_user(), None )
            for user, pn_ls in u_dict.items():
                for project_name, last_seen in pn_ls.items():
                    ### if not already reported as same calss by user itself
                    user_previous_report = get_user_previous_report( input_json['var_accepted'], input_json['assembly'], user.username, project_name )
                    if user_previous_report != var_user.reported:
                        add_var_user_notification_message( user, input_json['var_accepted'], var_user.reported, project_name, last_seen, user_previous_report )
        var_user.reported_YN = True
        var_user.reported_status = input_json['var_accepted_status']
        var_user.reported_on = datetime.utcnow()
        db.session.commit()
        return(jsonify({ 'insertion' : 'success' }))
    return(jsonify({ 'insertion' : 'fail' }))



def get_user_previous_report( variant_name, assembly, username, project_name ):
    var_user = get_var_user( variant_name, username, assembly, project_name )
    if var_user.reported_YN == True:
        return( var_user.reported )
    return( None )


def get_var_users( variant_name, assembly ):
    '''
        this is to get all users (obj) that found a variant
        and relative project_name : last_seen
    '''
    d = {}
    if assembly == 'hg19':
        var = VariantHG19.query.filter_by( name = variant_name ).first()
    elif assembly == 'hg38':
        var = VariantHG38.query.filter_by( name = variant_name ).first()
    for vu in var.variant_users.all():
        user = User.query.filter_by( id = vu.user_id ).first()
        if user not in d:
            d.update({ user : { vu.project_name : vu.last_seen }})
        else:
            d[user].update({ vu.project_name : vu.last_seen })
    return( d )



def add_var_user_notification_message( user, variant_name, var_acmg, project_name, last_seen, user_previous_report = None ):
    trans = ({
                'P' : 'Pathogenic',
                'LP' : 'Likely Pathogenic',
                'US' : 'Uncertain Significance',
                'LB' : 'Likely Benign',
                'B' : 'Benign'
    })
    if var_acmg not in trans:
        return(False)
    if user_previous_report:
        body = "Hi {0}! Please note that a variant ({1}) that you analyzed in your previous project: {2} and classified as {5}, has been reported as {3} by another user. Last time you checked it out was: {4}. Please have a look!".format( user.username, variant_name, project_name, trans[var_acmg], last_seen.strftime("%m-%d-%Y"), trans[user_previous_report] )
    else:
        body = "Hi {0}! Please note that a variant ({1}) that you analyzed in your previous project: {2} has been reported as {3} by another user. Last time you checked it out was: {4}. Please have a look!".format( user.username, variant_name, project_name, trans[var_acmg], last_seen.strftime("%m-%d-%Y") )
    msg = Message( recipient_id = user.id, body=body )
    db.session.add(msg)
    db.session.commit()
    return( True )



@check_variant_SQL_DB
def update_variant_user_SQL( username, variant_list, assembly, project_name ):
    '''
        this checks that the passed list of variants is linked to the relative user in the SQL DB
        and otherwise add the link
    '''
    for variant_name in variant_list:
        var_user = get_var_user( variant_name, username, assembly, project_name )
    return( True )



@bp.route('/get_known_variants', methods=['POST'])
@token_auth.login_required
def get_known_variants():
    '''
        this teturns the DICT with all known P/LP variants in the specified assembly
    '''
    input_json = request.get_json( force = True )
    username = token_auth.current_user().username
    if 'assembly' in input_json and 'project_name' in input_json:
        if input_json['assembly'] == 'hg19':
            token_auth.current_user().last_knownHG19_request = datetime.utcnow()
            token_auth.current_user().last_knownHG19_request_project_name = input_json['project_name']
            known_dict = get_known_variants_dict_v1()['hg19']
        elif input_json['assembly'] == 'hg38':
            token_auth.current_user().last_knownHG38_request = datetime.utcnow()
            token_auth.current_user().last_knownHG38_request_project_name = input_json['project_name']
            known_dict = get_known_variants_dict_v1()['hg38']
        db.session.commit()
        dictToReturn = ({ 'known_dict' : known_dict })
    else:
        dictToReturn = {}
    return(jsonify(dictToReturn))


@bp.route('/get_all_known_variants', methods=['POST'])
@token_auth.login_required
def get_all_known_variants():
    '''
        this teturns the DICT with ALL known P/LP variants
    '''
    input_json = request.get_json( force = True )
    username = token_auth.current_user().username
    known_dict = get_known_variants_dict_v1( username )
    token_auth.current_user().last_knownHG19_request = datetime.utcnow()
    token_auth.current_user().last_knownHG38_request = datetime.utcnow()
    dictToReturn = ({ 'known_dict' : known_dict })
    return(jsonify(dictToReturn))



def get_known_variants_dict_v1( USERNAME ) :
    '''
        this extract the known_dict from SQL DB
    '''
    d = ({ 'hg19' : {}, 'hg38' : {} })
    user = User.query.filter_by( username = USERNAME ).first()
    userID = user.id
    var19_id_list = VariantHG19User.query.filter( VariantHG19User.reported_YN == True).filter( VariantHG19User.user_id != userID ).all()
    for v in var19_id_list:
        if v.variant_id in d['hg19']:
            if v.reported_criteria in d['hg19'][v.variant_id]:
                d['hg19'][v.variant_id][v.reported_criteria] += v.reported_num
            else:
                d['hg19'][v.variant_id].update({ v.reported_criteria : v.reported_num })
        else:
            d['hg19'].update({ v.variant_id : { v.reported_criteria : v.reported_num } })
    var38_id_list = VariantHG38User.query.filter( VariantHG38User.reported_YN == True).filter( VariantHG38User.user_id != userID ).all()
    for v in var38_id_list:
        if v.variant_id in d['hg38']:
            if v.reported_criteria in d['hg38'][v.variant_id]:
                d['hg38'][v.variant_id][v.reported_criteria] += v.reported_num
            else:
                d['hg38'][v.variant_id].update({ v.reported_criteria : v.reported_num })
        else:
            d['hg38'].update({ v.variant_id : { v.reported_criteria : v.reported_num } })
    return(d)



def get_known_variants_dict() :
    '''
        this extract the known_dict from SQL DB
    '''
    d = ({ 'hg19' : {}, 'hg38' : {} })
    var19_id_list = VariantHG19User.query.filter_by( reported_YN = True ).all()
    for v in var19_id_list:
        variant = VariantHG19.query.filter_by( id = v.variant_id ).first()
        if variant.name in d['hg19']:
            if v.reported in d['hg19'][variant.name]:
                d['hg19'][variant.name][v.reported] += 1
            else:
                d['hg19'][variant.name].update({ v.reported : 1 })
        else:
            d['hg19'].update({ variant.name : { v.reported : 1 } })
    var38_id_list = VariantHG38User.query.filter_by( reported_YN = True ).all()
    for v in var38_id_list:
        variant = VariantHG38.query.filter_by( id = v.variant_id ).first()
        if variant.name in d['hg38']:
            if v.reported in d['hg38'][variant.name]:
                d['hg38'][variant.name][v.reported] += 1
            else:
                d['hg38'][variant.name].update({ v.reported : 1 })
        else:
            d['hg38'].update({ variant.name : { v.reported : 1 } })
    return(d)





'''
    this below is to return a dict with user variants in all assemblies
'''
'''
from flask_login import login_required
from flask import flash, render_template

@bp.route('/development_get_user_variants_dict/', methods=['GET'])
@login_required
def development_get_user_variants_dict():
    r = get_user_variants_dict( 'enrico0' )
    flash( r, 'info' )
    return(render_template('blank_DXcator.html'))


@check_variant_SQL_DB
def get_user_variants_dict( username ):
    r = { 'hg19' : {}, 'hg38' : {} }
    user = User.query.filter_by( username = username ).first_or_404()
    variantsHG19 = user.variantHG19_users.all()
    variantsHG38 = user.variantHG38_users.all()
    for var_user in variantsHG19:
        var = VariantHG19.query.filter_by( id = var_user.variant_id ).first()
        if var:
            r['hg19'].update({ var.name : var.id })
    for var_user in variantsHG38:
        r['hg38'].update({ i : 'NA' })
        var = VariantHG38.query.filter_by( id = var_user.variant_id ).first()
        if var:
            r['hg38'].update({ var.name : var.id })
    return( r )
'''


def get_var_user( variant_name, username, assembly, project_name ):
    '''
        this extrapolates var-user object based on assembly
        and creates the entry if not exists
    '''
    user = User.query.filter_by( username = username ).first_or_404()
    variant = get_var( variant_name, assembly )
    if assembly == 'hg19':
        var_user = VariantHG19User.query.filter_by( variant_id = variant.id, user_id = user.id, project_name = project_name ).first()
        if not var_user :
            var_user = VariantHG19User( variant_id = variant.id, user_id = user.id, project_name = project_name )
            db.session.add( var_user )
        else:
            var_user.last_seen = datetime.utcnow()
        db.session.commit()
    elif assembly == 'hg38':
        var_user = VariantHG38User.query.filter_by( variant_id = variant.id, user_id = user.id, project_name = project_name ).first()
        if not var_user :
            var_user = VariantHG38User( variant_id = variant.id, user_id = user.id )
            db.session.add( var_user )
        else:
            var_user.last_seen = datetime.utcnow()
        db.session.commit()
    return( var_user )


@check_variant_SQL_DB
def get_var( variant_name, assembly ):
    '''
        this extrapolates var object based on assembly
        and creates the entry if not exists
    '''
    if assembly == 'hg19':
        variant = VariantHG19.query.filter_by( name = variant_name ).first()
        ### if variant not in DB add it
        if not variant:
            variant = VariantHG19( name = variant_name )
            db.session.add( variant )
            db.session.commit()
    elif assembly == 'hg38':
        variant = VariantHG38.query.filter_by( name = variant_name ).first()
        ### if variant not in DB add it
        if not variant:
            variant = VariantHG38( name = variant_name )
            db.session.add( variant )
            db.session.commit()
    return( variant )
