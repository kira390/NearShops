# NearShops
## Authentication service
Since we have to handle users access to resources and Sessions are **"the evil"**, i've opted for the use of an OAuth2-like Tokens on JWT (JSON Web Token). any client have to sign in with the Auth service get a token and use it to get resources from the other services.
