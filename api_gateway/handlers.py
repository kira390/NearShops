import json
import os
from json import JSONDecodeError

import requests
from flask import make_response, jsonify
from flask_restful import abort


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
    try:
        if request.method == 'GET':
            resp = requests.get(url,json=request.json, headers=request.headers)
            return make_response(xjson(resp), resp.status_code)
        elif request.method == 'POST':
            resp = requests.post(url, json=request.json, headers=request.headers)
            return make_response(xjson(resp), resp.status_code)
        elif request.method == 'PUT':
            resp = requests.put(url, json=request.json, headers=request.headers)
            return make_response(xjson(resp), resp.status_code)
        elif request.method == 'DELETE':
            resp = requests.delete(url, json=request.json, headers=request.headers)
            return make_response(xjson(resp), resp.status_code)
    except requests.ConnectionError:
        pass
    return abort(404, message="this Resource is not available.")

def xjson(response):
    try:
        return jsonify(response.json())
    except JSONDecodeError:
        if str(response.status_code).startswith("5"):
            return abort(404, message="this Resource is not available.")
        return response.text
