# NearShops
## Architecture
Since for me this challenge is an other opportunity to learn i designed the app as a distributed application to make it more challenging. and make the application scallable and fault telerant using service replication and automate the deployement process using Docker/Swarm/Kubernetes.

It is composed of 3 REST-based microservices:
* Authentication service
* Shop service
* API Gateway

### Authentication service
Since we have to handle users access to resources and Sessions are **"the evil"**, i've opted for the use of an OAuth2-like Tokens on JWT (JSON Web Token). any client have to sign in with the Auth service get a token and use it to get resources from the other services.

### Shop service
This is is the main service: Receives requests from clients, check their token if it's valid sends the right response. this service make available the following endpoints:
|Endpoints|Operations|Description|
|---------|----------|-----------|
|/shops/|GET|     |
|/shops/|POST|     |
|/shops/<ShopID>|GET|     |
|/shops/<ShopID>|PUT|     |
|/shops/<ShopID>|DELETE|     |
