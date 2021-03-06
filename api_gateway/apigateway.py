from flask import Flask, request
from flask_restful import abort
from handlers import *


app = Flask(__name__)
configure_envirement(app)





@app.errorhandler(404)
def error_handler(code):
    abort(404, message="this Resource is not available.")


@app.route("/<path:code>",methods=["GET","POST","PUT","DELETE"])
def main(code):
    for key, value in app.config["API_BINDS"].items():
        if code.startswith(key):
            return redirection_handler(value,request)
    return error_handler(request)


if __name__ == '__main__':
    app.run(port=app.config['APP_PORT'], host=app.config['APP_BIND'], debug=True)