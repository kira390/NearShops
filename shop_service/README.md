# NearShops
## Shop service
This is is the main service: It Receives requests from clients, check their token if it's valid sends the right response.

## Shop Service REST operations
Following are the REST operations available to use Shop Service.

An Authentication is required for all those operations a Token must be added to the header of the HTTP request. 

|Operation|	HTTP action|Description|
|-----------------------------------------------------------------------------------|------------------------|---------------------------------------------------|
|List all shops, sort them by proximity if **longitude** and **latitude** are given.|GET /shops              |HTTP Code: 200 on success.<br/>Output: JSON.       |
|Adding a Shop (requires admin privileges).                                         |POST /shops             |HTTP Code: 201 on success.<br>Input: JSON payload. |
|Get a Shop by ShopID.                                                              |GET /shops/**shopID**   |HTTP Code: 200 on success.<br/>Output: JSON.       |
|Updating shop (requires admin privileges).                                         |PUT /shops/**shopID**   |HTTP Code: 204 on success.<br/>Input: JSON payload.|
|Deleting a shop (requires admin privileges).                                       |DELETE /shops/**shopID**|HTTP Code: 204 on success                          |

## Shop Format
Here is a sample of how a shop document looks like:
```json
{
    "_id": "5b37a3d2c24feb54f92358f3",
    "name": "MOTOBOX",
    "address": "104 Boulevard Omar Al Khiam, Casablanca 20850",
    "longitude": 33.562979,
    "latitude": -7.648566,
    "likers": ["kira390@gmail.com", "malij14@outlook.fr"],
    "dislikers": [{
        "login": "trop1@gmail.com",
        "timestamp": "1530317635.3212626"
    }]
}
```