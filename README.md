# NearShops
This project is [The Web Coding Challenge](https://github.com/hiddenfounders/web-coding-challenge/blob/master/README.md) proposed Hidden Founders as part of their hiring process.

More infos on the guidelines are [here](https://github.com/hiddenfounders/web-coding-challenge/blob/master/coding-challenge.md)

## Objectives
My objectives here are to build the Backend endpoints for an app that lists shops nearby.

The features offered by the project are:
* Handling the user Sign up/Sign in processes

Signed in users can:
* Retrieve nearby shops (Sorted by distance).
* Like shops (liked shops won't appear in the nearby shops).
* Retrieve the liked shops list.
* Remove a shops from his liked shops list
* Dislike shops (disliked shops won't appear in the nearby shops for 2 hours).

## Architecture
Since for me this challenge is an other opportunity to learn i've designed the app as a distributed application to make it more challenging. and make the application scallable and fault telerant using service replication and automate the deployement process using Docker/Swarm/Kubernetes.

It is composed of 3 REST-based microservices:
* [Authentication service](shop_service/README.md)
* [Shop service](authentication_service/README.md)
* [API Gateway](api_gateway/README.md)

##Dependencies
* [Python](https://www.python.org/)
* [Flask](http://flask.pocoo.org/)
* [Flask-Restful](https://flask-restful.readthedocs.io/en/latest/)
* [PyMongo](https://api.mongodb.com/python/current/)
* [MockupDB](http://mockupdb.readthedocs.io/)
* [PyJWT](https://pypi.org/project/PyJWT/1.4.0/)
* [geopy](https://geopy.readthedocs.io/en/stable/)
* [cryptography](https://cryptography.io/en/latest/)
* [Docker](https://www.docker.com/)
