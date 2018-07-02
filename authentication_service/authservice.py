from flask import Flask
from flask_restful import Api

from common import configure_envirement
from resources import SignIn, SignUp

app = Flask(__name__)
api = Api(app)

configure_envirement(app)

api.add_resource(SignIn,"/auth/signin","/auth/signin/",resource_class_kwargs={"app":app})
api.add_resource(SignUp, "/auth/signup","/auth/signup/",resource_class_kwargs={"app":app})

if __name__ == '__main__':
    app.run(port=app.config['APP_PORT'], host=app.config['APP_BIND'])