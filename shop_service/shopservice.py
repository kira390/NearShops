from flask import Flask
from flask_restful import Api

from shop_service.common import APP_PORT,APP_BIND
from shop_service.resources import *

app = Flask(__name__)
api = Api(app)

api.add_resource(ShopsDisliked,'/shops/disliked','/shops/disliked/')
api.add_resource(ShopsLiked,'/shops/liked','/shops/liked/')
api.add_resource(Shop,'/shops/<string:shop_id>')
api.add_resource(Shops,'/shops')
if __name__ == '__main__':
    app.run(port=APP_PORT, host=APP_BIND, debug=True)