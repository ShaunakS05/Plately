import os
from pymongo import MongoClient
from MenuClasses import MenuItem 
import random

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Plately:Plately@platelycluster.loy8l.mongodb.net/?retryWrites=true&w=majority&appName=PlatelyCluster")
DB_NAME = "PlatelyData"
MENUITEMS_COLLECTION_NAME = "MenuItems"
SEGMENT_COLLECTION_NAME = "SEGMENTS"

def fetch_menu_from_mongo():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[MENUITEMS_COLLECTION_NAME]

        menu_data = collection.find_one({}, {"_id": 0})

        # if not menu_data:
        #     return generate_fake_menu()
        
        menu_items = []
        for category, items in menu_data.items():
            for idx, item in enumerate(items):
                dish_id = f"{category[:2].upper()}{idx + 1:03}"
                menu_items.append(
                    MenuItem(
                        dish_id=dish_id,
                        name=item["name"],
                        price=item["price"],
                        cost=item["cost"],
                        quantity_sold=item["quantity_sold"],
                        portion_size=random.randint(150, 400), 
                    )
                )
        return menu_items
    
    except Exception as e:
        print("type")


def fetch_segments_from_mongo():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[SEGMENT_COLLECTION_NAME]

        segment_data = collection.find_one({}, {"_id": 0})

        return segment_data["segments"]
    except Exception as e:
        print("type")