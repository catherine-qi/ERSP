from pymongo import MongoClient
cluster = "mongodb://localhost:27017"
client = MongoClient(cluster)

print(client.list_database_names())

db = client.ERSP
print(db.list_collection_names())
