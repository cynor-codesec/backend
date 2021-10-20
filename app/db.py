import pymongo

uri = "mongodb://cynor:CzumGzsYO7oNtI7jrUeHxq5u4bPDJEB2JomxknVsAFDLsZRUZXwMvVOIKq7sDfScfjM0BCKcTgreceTSWeEXpQ==@cynor.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@cynor@"
client = pymongo.MongoClient(uri)

database = client['cynor']

sessions_collection = database["sessions"]
cv_collection = database["cvInfo"]

print("Connected to the db")