import requests
from flask import Response, make_response, jsonify, Request


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


