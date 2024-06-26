import flask
from typing import Dict
import os

import main

application = flask.Flask(__name__)

@application.route('/')
def hello():
    return "RepoAPI"

@application.route('/process')
def repoapi_entry():
    
    auth_header = flask.request.headers.get('Authorization')
    
    if not auth_header:
        flask.abort(401, description="Authorization header is missing")

    parts = auth_header.split()
    
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        flask.abort(401, description="Authorization header must be Bearer token")

    api_key = parts[1]
    if api_key != os.environ.get('REPOAPI_MODAL_KEY'):
        print("Invalid API key request")
        flask.abort(403, description="Invalid API key")

    input: Dict = flask.request.json
    print(input)
    repo_link = input['repo_link']
    docker_link = input['docker_link']
    apis = input['apis']
    apis = apis.split(',')
    apis = [api.lstrip().rstrip() for api in apis]
    gpu_type = input['gpu_type'].upper()
    
    try:
        run_result = main.run(repo_link, docker_link, apis, gpu_type)
    except:
        return flask.jsonify({'status': '500', 'data': run_result})

    if run_result:
        return flask.jsonify({'status': '500', 'data': run_result})
    return flask.jsonify({'status': '200'})

if __name__ == '__main__':
    application.run()
