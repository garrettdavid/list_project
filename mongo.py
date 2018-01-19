from pymongo import MongoClient

def insert(name, hash):
    client = MongoClient()
    db = client.users
    users = db.users
    users.insert_one("username": name, "hash": hash)
    db.close();