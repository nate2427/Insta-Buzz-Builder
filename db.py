from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json

 # Loads the config
with open('config.json') as config_file:
    data = json.load(config_file)

MONGO_DB_URI = data['MONGODB_URI']
MONGO_DB_PWD = data['MONGODB_PWD']
MONGODB_USER = data['MONGODB_USER']

uri = f"mongodb+srv://{MONGODB_USER}:{MONGO_DB_PWD}@{MONGO_DB_URI}"

client = MongoClient(uri, server_api=ServerApi('1'))
db = client.Reddit

# Get the persona collection
persons = db.persona_configs


def get_all_personas():
    persona_configs = []
    try:
        # dont return the _id field
        persona_configs = list(persons.find({}, {"_id": 0}))
        personas = {}
        for persona_config in persona_configs:
            personas[persona_config['persona_name']] = persona_config['persona_template_id']
        return personas
    except Exception as e:
        print(e)
        return persona_configs