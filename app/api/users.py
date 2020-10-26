from app.api import bp
from flask import jsonify
from app.models import User
from flask import request
from flask import url_for
from app.api.errors import bad_request, error_response
from app import db
from flask_httpauth import HTTPBasicAuth
from app.api.auth import token_auth
from flask import abort

basic_auth = HTTPBasicAuth()


@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user


@basic_auth.error_handler
def basic_auth_error(status_code):
    return error_response(status_code)


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100) # We set a maximum as we do not want the client to control that
    data = User.to_collection_dict(query=User.query, page=page, per_page=per_page, endpoint='api.get_users')
    return jsonify(data)


@bp.route('/users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(query=user.followers, page=page, per_page=per_page, endpoint='api.get_followers', id=id)
    return jsonify(data)


@bp.route('/users/<int:id>/following', methods=['GET'])
@token_auth.login_required
def get_following(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(query=user.followed, page=page, per_page=per_page, endpoint='api.get_following', id=id)
    return jsonify(data)


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        bad_request("username, email and password fields are required")
    if User.query.filter_by(username=data['username']).first():
        bad_request("username already exists, please use another username")
    if User.query.filter_by(email=data['email']).first():
        bad_request("email already exists, please use another email")

    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict(include_email=True))
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def modify_user(id):
    if token_auth.current_user().id != id:
        abort(403)
    data = request.get_json() or {}
    user = User.query.get_or_404(id)

    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        bad_request("username already exists, please use another username")

    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        bad_request("email already exists, please use another email")

    user.from_dict(data)
    db.session.commit()
    return jsonify(user.to_dict(include_email=True))
