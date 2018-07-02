import json
import os

import requests
from flask import Response, make_response, jsonify, Request

def configure_envirement(app):
    app.config['APP_BIND'] = "0.0.0.0"
    app.config['APP_PORT'] = 80
    app.config["API_BINDS"] = '{"shops":"http://shopservice","auth": "http://authservice"}'
    for key in app.config.keys():
        if key in os.environ:
            app.config[key]=os.environ[key]
    app.config["API_BINDS"]=json.loads(app.config["API_BINDS"])

def redirection_handler(url, request):
    url = url+request.full_path
    if request.method == 'GET':
        resp = requests.get(url,json=request.json, headers=request.headers)
        return make_response(jsonify(resp.json()), resp.status_code)
    elif request.method == 'POST':
        resp = requests.post(url, json=request.json, headers=request.headers)
        return make_response(jsonify(resp.json()), resp.status_code)
    elif request.method == 'PUT':
        resp = requests.put(url, json=request.json, headers=request.headers)
        return make_response(jsonify(resp.json()), resp.status_code)
    elif request.method == 'DELETE':
        resp = requests.delete(url, json=request.json, headers=request.headers)
        return make_response(jsonify(resp.json()), resp.status_code)
    return make_response(jsonify(
        {
            "message": "this Resource is not available."
        }
    ), 404)


