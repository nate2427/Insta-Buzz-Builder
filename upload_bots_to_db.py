# uses mongodb to store bot info

# object = {"insta_name": "", "insta_pwd": "", "email_name": "", "email_pwd": "", "insta_in_use": False}

# need to take the file name from the command line and open it. It is a text file in the following format for each line: YAHOO MAIL	PASSWORD	USERNAME INSTAGRAM	PASSWORD

# each entry is a line in the file.


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json, sys

# Loads the config
with open('config.json') as config_file:
    data = json.load(config_file)

uri = f"mongodb+srv://{data['MONGODB_USER']}:{data['MONGODB_PWD']}@{data['MONGODB_URI']}"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

def main():
    # take filename from command line
    file_name = sys.argv[1]

    accounts = []

    # open the text file
    with open(file_name) as file:
        for line in file:
            # split the line into a list
            line = line.split("\t")

            # get the email
            email = line[0].strip()
            # get the email password
            email_password = line[1].strip()
            # get the instagram username
            insta_username = line[2].strip()
            # get the instagram password
            insta_pwd = line[3].strip()

            obj = {
                "insta_name": insta_username,
                "insta_pwd": insta_pwd,
                "email_name": email,
                "email_pwd": email_password,
                "insta_in_use": False
            }
            # add to accounts as an obj
            accounts.append(obj)

    # save the accounts to the database
    db = client["Bots"]
    collection = db["Social Media Bots"]

    return collection.insert_many(accounts)
