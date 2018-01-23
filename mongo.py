#from pymongo import MongoClient
import pymongo
import sys

class User:
    def __init__(self, username, hash):
        self.username = username
        self.hash = hash

try:
    client = pymongo.MongoClient()
    print("Connected successfully!")
except:
    print("Could not connect to MongoDB")

def db_insert(new_user):
    entry = { "username": new_user.username, "hash": new_user.hash}
    db = client.test_db
    users = db.users
    result = users.insert_one(entry)
    return result