from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json, os
from dotenv import load_dotenv
load_dotenv()

 # Loads the config
with open('config.json') as config_file:
    data = json.load(config_file)


MONGO_DB_URI = os.getenv("MONGODB_URI")
MONGO_DB_PWD = os.getenv("MONGODB_PWD")
MONGODB_USER = os.getenv("MONGODB_USER")


uri = f"mongodb+srv://{MONGODB_USER}:{MONGO_DB_PWD}@{MONGO_DB_URI}"

client = MongoClient(uri, server_api=ServerApi('1'))
db = client.Reddit

# Get the persona collection
personas = db.persona_configs
    

def add_new_persona_config(persona_name, persona_template_id):
    new_persona_config = {
        "persona_name": persona_name,
        "persona_template_id": persona_template_id
    }
    try:
        personas.insert_one(new_persona_config)
        return True
    except Exception as e:
        print(e)
        return False

def get_all_persona_configs():
    persona_configs = []
    try:
        # dont return the _id field
        persona_configs = list(personas.find({}, {"_id": 0}))
        _personas = {}
        for persona_config in persona_configs:
            _personas[persona_config['persona_name']] = persona_config['persona_template_id']
        return _personas
    except Exception as e:
        print(e)
        return persona_configs