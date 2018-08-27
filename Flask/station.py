from pymongo import MongoClient

def get_station():
    username="paul0115"
    password="paul0115"
    client = MongoClient('mongodb://%s:%s@175.119.200.201/default_db?authSource=admin' % (username, password))
    return client.ddarungDB.station
