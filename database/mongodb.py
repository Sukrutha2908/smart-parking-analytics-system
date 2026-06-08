from pymongo import MongoClient
uri = "mongodb+srv://veeramaheswarijayampu:mahi%40thk7@pkslotcluster.9s8rgmc.mongodb.net//?retryWrites=true&w=majority"

client = MongoClient(uri)

db = client["smart_parking_db"]

print("Connected to MongoDB Atlas!")