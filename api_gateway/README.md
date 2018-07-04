# NearShops
## API Gateway

This service is just a simple API Gateway it gives a layer of abstraction. it takes a json object as a environment variable.

## APP_BINDS format

I kept it very basic since the objective is not building a full-fledged API Gateway. 

````json
{
  "shops":"http://localhost:5001", # redirect all path starting with shops to the shop service
  "auth": "http://localhost:5000" # redirect all path starting with auth to the authentication service
}
````
