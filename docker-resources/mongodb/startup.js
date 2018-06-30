db = db.getSiblingDB('admin')
db.createUser(
    {
        user: "shopproxy",
        pwd: "azerty",
        roles: [ "root" ]
    }
)
db = db.getSiblingDB('shopservice')
db.shops.insert(
    {
        name: "MOTOBOX",
        address: "104 Boulevard Omar Al Khiam, Casablanca 20850",
        longitude: 33.562979,
        latitude: -7.648566,
        likers: ["kira390","malij14"],
        dislikers: [{login:"trop1", timestamp:"1530317635.3212626"}]
    }
)
db.shops.insert(
    {
        name: "La Table Des Sens",
        address: "352,Boulevard Abdelmoumen, Quartier France Ville., (Croisement Boulevard Abdelmoumen & Boulevard Ghandi, Casablanca 20000",
        longitude: 33.564474,
        latitude: -7.627349,
        likers: ["trop1","malij14"],
        dislikers: [{login:"kira390", timestamp:"1530317635.3212626"}]
    }
)
db.shops.insert(
    {
        name: "Restaurant Zayna",
        address: "104 Boulevard Omar Al Khiam, Casablanca 20850",
        longitude: 33.577321,
        latitude: -7.607404,
        likers: ["kira390","trop1"]
    }
)

db = db.getSiblingDB('authservice')
db.users.insert(
    {
        login: "kira390",
        password: "123456",
        role: "admin"
    }
)
db.users.insert(
    {
        login: "malij14",
        password: "123456",
        role: "regular"
    }
)
db.users.insert(
    {
        login: "trop1",
        password: "123456",
        role: "regular"
    }
)

db.clients.insert(
    {
        client_id: "midleware1",
        client_secret: "1sfg135df1d32fsdf489d7q6sdq6s4d"
    }
)
db = db.getSiblingDB('admin')
db.shutdownServer()