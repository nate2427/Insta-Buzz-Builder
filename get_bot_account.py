from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# Loads the config
with open('config.json') as config_file:
    data = json.load(config_file)

uri = f"mongodb+srv://{data['MONGODB_USER']}:{data['MONGODB_PWD']}@{data['MONGODB_URI']}"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

def main():
    db = client["Bots"]
    collection = db["Social Media Bots"]
    # find and return one bot that is not in use and set it as in use
    bot = collection.find_one({"insta_in_use": False})
    bot["insta_in_use"] = True
    # update the bot
    collection.update_one({"_id": bot["_id"]}, {"$set": bot})
    return JSONEncoder().encode(bot)

if __name__ == '__main__':
    main()