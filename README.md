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
* [Authentication service](authentication_service/README.md)
* [Shop service](shop_service/README.md)
* [API Gateway](api_gateway/README.md)

## Dependencies
* [Python](https://www.python.org/)
* [Flask](http://flask.pocoo.org/)
* [Flask-Restful](https://flask-restful.readthedocs.io/en/latest/)
* [PyMongo](https://api.mongodb.com/python/current/)
* [MockupDB](http://mockupdb.readthedocs.io/)
* [PyJWT](https://pypi.org/project/PyJWT/1.4.0/)
* [geopy](https://geopy.readthedocs.io/en/stable/)
* [cryptography](https://cryptography.io/en/latest/)
* [Docker](https://www.docker.com/)

## Testing

Unit tests are available for the authentication service (more than 95% coverage), i'll try to make some for the other services,
the gateway is very simple it's mainly just two functions. tests are more like integration tests because they not only tests 
the classes but also the wiring, i mocked mongodb requests using mockupdb that i discovered last night we spen a long night together
and unittest nothing realy fancy.

## Deployement
PS: THIS APP IS NOT MEANT FOR PRODUCTION 

This application is easly deployable using:
 * docker-compose: just download the project and run **docker-compose up**
 * docker Swarm: just run
  
            docker swarm init #starts a swarm manager
            docker stack deploy -c docker-compose.yml nearshops #deploys the application

by default it will start 
* 5 Shop service containers
* 3 Authentication service instances
* 2 Api Gateway

For simplicity i kept a single mongodb instance a mongodb cluster can be set on production.<br>
since all the services are stateless load balancing is handled by docker (roun robin) in a seamless way between services.
If deployed on swarm containers are set to respawn on failure.

## My impressions
Well looking back those few days so much new things learned, as a python noob and technology lover this experience was for me a real pleasurable challenge. 
Tt's surely not the best app nor the most complete i'll try to keep improving it the next days. 
To summarize it was indeed an **Adventure** with all its joy and frustrations.
Finaly i apologies for all the typos i realy look like a zombie right now.

        
   