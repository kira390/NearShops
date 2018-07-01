from flask import Flask, request
from api_gateway.handlers import *

app = Flask(__name__)

app.config["binds"]={
    "shops":"http://localhost:5001",
    "auth":"http://localhost:5000"
}

APP_BIND='localhost'
APP_PORT= 5002

@app.errorhandler(404)
def error_handler(code):
    return make_response(jsonify(
        {
            "message": "this Resource is not available."
        }
    ), 404)


@app.route("/<path:code>",methods=["GET","POST","PUT","DELETE"])
def main(code):
    for key, value in app.config["binds"].items():
        if code.startswith(key):
            return redirection_handler(value,request)
    return error_handler(request)


if __name__ == '__main__':
    app.run(host=APP_BIND, port=APP_PORT, debug=True)