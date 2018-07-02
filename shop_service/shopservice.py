from flask import Flask
from flask_restful import Api

from resources import *
from common import configure_envirement

app = Flask(__name__)
api = Api(app)

configure_envirement(app)


api.add_resource(ShopsDisliked,'/shops/disliked', '/shops/disliked/', resource_class_kwargs={"app":app})
api.add_resource(ShopsLiked,'/shops/liked', '/shops/liked/', resource_class_kwargs={"app":app})
api.add_resource(Shop,'/shops/<string:shop_id>', resource_class_kwargs={"app":app})
api.add_resource(Shops, '/shops',resource_class_kwargs={"app":app})
if __name__ == '__main__':
    app.run(port=app.config['APP_PORT'], host=app.config['APP_BIND'], debug=True)