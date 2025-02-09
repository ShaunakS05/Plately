from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import MongoClient
import pymongo
print(pymongo.__version__)


# MongoDB connection URI
uri = "mongodb+srv://Plately:Plately@platelycluster.loy8l.mongodb.net/?retryWrites=true&w=majority&appName=PlatelyCluster"

# Connect to MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))

# Select database and collection
db = client["PlatelyDatabase"]  # Change to your actual database name
collection = db["MenuItems"]    # Create or select a collection

menu_item = {
    "name": "Avocado Toast",
    "category": "Breakfast",
    "price": 8.99,
    "ingredients": ["Avocado", "Bread", "Egg", "Tomato"],
    "calories": 350
}

insert_result = collection.insert_one(menu_item)
print(f"Inserted document with ID: {insert_result.inserted_id}")