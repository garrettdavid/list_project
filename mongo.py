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

def db_insert_user(new_user):
    entry = { "username": new_user.username, "hash": new_user.hash, "lists": []}
    db = client.test_db
    result = db.users.insert_one(entry)
    return result

def db_search(username):
    db = client.test_db
    result = db.users.find_one({"username": username})
    return result

#def db_newlist(list_name):
#    db = client.test_db
#    result = db.users.find_one({"_id": session["user_id"]})