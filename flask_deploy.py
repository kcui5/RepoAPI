import flask
from typing import Dict
import os

import main

app = flask.Flask(__name__)

@app.route('/')
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
    apis = input['apis']
    apis = apis.split(', ')
    args = {
        apis[0]: input['args'].split(', ')
    }
    gpu_type = ""
    main.from_local_package(repo_link, apis, args, gpu_type)
    return flask.jsonify({'status': '200'})

if __name__ == '__main__':
    app.run(debug=True)
