from flask import Flask, request, jsonify, session, abort

from .utilities import crossdomain

import os
import sys
from functools import wraps

application = app = Flask(__name__)

# Read configuration variables from the environment.
env_var_prefix = 'DISTRIBUTORG_'
for var_name, value in os.environ.items():
    if var_name.startswith(env_var_prefix):
        app.config[var_name[len(env_var_prefix):]] = value

# Verify the required configuration variables.
required_configuration_variables = ['SECRET_KEY', 'EMAIL', 'PASSWORD', 'ORG_FILE_PATH']
for variable in required_configuration_variables:
    if variable not in app.config:
        print('Missing config variable %s' % (variable,))
        sys.exit(2)

def signin_required(f):
    '''
    Decorator for view functions that require the user to be signed in.
    '''
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if not session.get('signed_in', False):
        #     abort(401)
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def test():
    return jsonify(success=True)

@app.route('/signin', methods=['POST', 'OPTIONS'])
@crossdomain(origin='http://localhost:8080', headers='Content-Type')
def signin():
    try:
        email = request.get_json()['email']
        password = request.get_json()['password']
    except (KeyError, TypeError):
        abort(401)

    if email != app.config['EMAIL'] or password != app.config['PASSWORD']:
        abort(403)
    
    session['signed_in'] = True

    return jsonify(success=True)

@app.route('/org_file', methods=['GET'])
@crossdomain(origin='http://localhost:8080', headers='Content-Type')
@signin_required
def get_org_file():
    with open(app.config['ORG_FILE_PATH'], 'r') as org_file:
        org_file_contents = org_file.read()

    return jsonify(org_file=org_file_contents)

@app.route('/org_file', methods=['PUT', 'OPTIONS'])
@crossdomain(origin='*', headers='Content-Type')
@signin_required
def update_org_file():
    try:
        new_org_file_contents = request.get_json()['org_file']
    except (KeyError, TypeError):
        abort(401)

    with open(app.config['ORG_FILE_PATH'], 'w') as org_file:
        org_file.write(new_org_file_contents)
    
    return jsonify(success=True)
