import flask
from typing import Dict

import main

app = flask.Flask(__name__)

@app.route('/')
def repoapi_entry():
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
