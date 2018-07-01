from flask import Flask
from flask_restful import Api

from authentication_service.resources import SignUp,SignIn

app = Flask(__name__)
api = Api(app)

app.config['MONGO_DBNAME']='authservice'
app.config['MONGO_URI']='mongodb://shopproxy:azerty@localhost:27017/'
app.config['PRIVATE_KEY'] = 'private.pem'
app.config['PUBLIC_KEY'] = 'public.pem'
app.config['AUTH_ALGO'] = 'RS256'
app.config['AUTH_HOST'] = 'localhost'
app.config['TOKEN_TTL'] = 20


APP_BIND = 'localhost'
APP_PORT = 5000


api.add_resource(SignIn,"/auth/signin","/auth/signin/",resource_class_kwargs={"app":app})
api.add_resource(SignUp, "/auth/signup","/auth/signup/",resource_class_kwargs={"app":app})
if __name__ == '__main__':
    app.run(port=APP_PORT, host=APP_BIND, debug=True)