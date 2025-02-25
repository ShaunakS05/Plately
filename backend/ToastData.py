from MenuClasses import MenuItem, Combo, OrderItem, OrderCombo, Order
from datetime import datetime, timedelta
import random, requests
import logging
from typing import List
from mongo import fetch_menu_from_mongo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create realistic combos
def generate_fake_combos(menu_items):
    return [
        Combo(combo_name="Appetizer + Entree", items=[menu_items[0].dish_id, menu_items[5].dish_id], price=15.00, quantity_sold=random.randint(40, 80)),
        Combo(combo_name="Soup + Entree", items=[menu_items[10].dish_id, menu_items[6].dish_id], price=16.00, quantity_sold=random.randint(50, 70)),
        Combo(combo_name="Family Special", items=[menu_items[2].dish_id, menu_items[4].dish_id, menu_items[9].dish_id], price=30.00, quantity_sold=random.randint(30, 60)),
    ]


def get_season(month):
    if(month == 1 or month == 2 or month == 12):
        return "Winter"
    elif(month == 3 or month == 4 or month == 5):
        return "Spring"
    elif(month == 6 or month == 7 or month == 8):
        return "Summer"
    elif(month == 9 or month == 10 or month == 11):
        return "Fall"
    logging.warning(f"Unknown month {month} detected in get_season(). Returning 'Unknown'.")
    return "Unknown"  # ✅ Fix the typo and add a log warning


# Generate fake orders
def generate_fake_orders(menu_items, combos, num_orders=1000):
    """
    Generate a list of fake orders for testing and analytics.
    
    Args:
        menu_items (list): List of MenuItem objects.
        combos (list): List of Combo objects.
        num_orders (int): Number of fake orders to generate.

    Returns:
        list: A list of Order objects.
    """
    orders = []
    now = datetime.now()

    possible_guest_names = [
        "John Doe", "Jane Smith", "Alex Johnson",
        "Wei Zhang", "Ling Chen", "Chris Brown"
    ]
    possible_addresses = [
        None, "123 Main St", "456 Elm St",
        "789 Maple Ave", "101 Pine Rd"
    ]
    possible_special_instructions = [
        None, "Extra spicy", "No peanuts",
        "Gluten-free", "Less salt", "No MSG"
    ]
    dining_options = ["dine-in", "takeout", "delivery"]

    for _ in range(num_orders):
        # 1. Pick a random day within the last 30 days
        day_offset = random.randint(0, 29)
        # 2. Pick a random time between 11:00 and 23:00 (11 AM to 11 PM)
        random_hour = random.randint(11, 23)
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)
        random_month = random.randint(1,12)

        # Build the date/time (subtracting 'day_offset' days from 'now')
        random_date = (now - timedelta(days=day_offset)).date()
        order_time = datetime(
            year=random_date.year,
            month=random_date.month,
            day=random_date.day,
            hour=random_hour,
            minute=random_minute,
            second=random_second
        )

        # 3. Determine season and day of the week
        order_season = get_season(random_month)
        if order_season == "Unknown":
            logging.warning(f"Order generated with unknown season. Order timestamp: {order_time}")

        order_day = order_time.strftime("%A")  # Monday, Tuesday, etc.

        # 4. Randomly select items
        selected_items = random.sample(menu_items, random.randint(1, 5))
        order_items = []
        for item in selected_items:
            order_items.append(
                OrderItem(
                    dish_id=item.dish_id,
                    quantity=random.randint(1, 4),
                    special_instructions=random.choice(possible_special_instructions)
                )
            )

        # 5. Randomly select combos
        selected_combos = random.sample(combos, random.randint(0, len(combos)))
        order_combos = []
        for combo in selected_combos:
            order_combos.append(
                OrderCombo(
                    combo_name=combo.combo_name,
                    quantity=random.randint(1, 2)
                )
            )

        # 6. Create the Order object
        order = Order(
            order_id=f"ORDER{random.randint(10000,99999)}",
            dining_option=random.choice(dining_options),
            items=order_items,
            combos=order_combos if order_combos else None,
            guest_name=random.choice(possible_guest_names),
            delivery_address=random.choice(possible_addresses),
            order_timestamp=order_time.isoformat(),
            season=order_season,  # ✅ Fixed: Now properly assigned
            day=order_day
        )
        orders.append(order)

    return orders


def fetch_menu_items():
    try:
        response = requests.get(f"{TOAST_API_BASE_URL}/menu", timeout=5)
        response.raise_for_status()
        data = response.json()
        return [MenuItem.model_validate(m) for m in data]
    except Exception as e:
        logger.warning("Failed to fetch menu from Toast API (%s). Using local fake menu data.", e)
        return fetch_menu_from_mongo()

def fetch_combos():
    try:
        response = requests.get(f"{TOAST_API_BASE_URL}/combos", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning("Failed to fetch combos from Toast API (%s). Using local fake combos data.", e)
        # If generate_fake_combos needs menu_items, you might call fetch_menu_items() first.
        return generate_fake_combos(fetch_menu_items())



def calculate_heat_scores_d3(menu_item_id: str, orders: List[Order]) -> dict:
    """
    Calculate heat score grids in D3 heatmap format for a given menu item across seasons.
    
    Assumes a global variable 'orders' exists, which is a list of order objects.
    Each order must have:
      - order.order_timestamp: ISO-formatted timestamp.
      - order.season: A string representing the season ("Winter", "Spring", etc.)
      - order.items: A list of order items, where each order item has:
            * dish_id: The menu item identifier.
            * quantity: The number ordered.
    
    The heat score grid is built for each season with 7 columns (days) and 6 rows (time buckets):
    
      Time Buckets:
        Bucket 0: 11:00 - 12:59   (label: "11-1")
        Bucket 1: 13:00 - 14:59   (label: "1-3")
        Bucket 2: 15:00 - 16:59   (label: "3-5")
        Bucket 3: 17:00 - 18:59   (label: "5-7")
        Bucket 4: 19:00 - 20:59   (label: "7-9")
        Bucket 5: 21:00 - 22:59   (label: "9-11")
    
    For each season, the raw counts are normalized (linearly scaled) so that the lowest
    count becomes 1 and the highest becomes 10. In the case where all counts are equal
    (or no orders exist for the menu item), a constant value is used.
    
    The returned dictionary maps each season to an array of objects in the D3 format:
    
        {
          "Winter": [
            { "x": "Monday", "y": "11-1", "value": 7 },
            { "x": "Monday", "y": "1-3", "value": 5 },
            { "x": "Tuesday", "y": "11-1", "value": 3 },
            ...
          ],
          "Spring": [...],
          "Summer": [...],
          "Fall": [...]
        }
    
    Args:
        menu_item_id (str): The menu item ID to analyze.
    
    Returns:
        dict: A dictionary mapping season names to D3 heatmap formatted data arrays.
    """
    # Define the seasons and days of the week.
    seasons = ["Winter", "Spring", "Summer", "Fall"]
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Define time bucket boundaries (hour ranges) and labels.
    # Each bucket is defined as [start_hour, end_hour), meaning it includes start_hour up to (but not including) end_hour.
    bucket_boundaries = [(11, 13), (13, 15), (15, 17), (17, 19), (19, 21), (21, 23)]
    bucket_labels = ["11-1", "1-3", "3-5", "5-7", "7-9", "9-11"]
    
    # This dictionary will eventually map each season to its D3 data array.
    season_d3_data = {}
    
    # Use the global orders list.
    
    for season in seasons:
        # Initialize a raw count grid for the current season.
        # Each day (key) maps to a list of six zero counts (one per time bucket).
        heat_counts = { day: [0] * 6 for day in days_of_week }
        
        # Process each order.
        for order in orders:
            if order.season != season:
                continue  # Skip orders not in the current season.
            
            for order_item in order.items:
                if order_item.dish_id != menu_item_id:
                    continue  # Only count orders for the specified menu item.
                
                try:
                    order_dt = datetime.fromisoformat(order.order_timestamp)
                except Exception:
                    continue  # Skip invalid timestamps.
                
                # Determine the day of the week.
                day_name = order_dt.strftime("%A")
                if day_name not in heat_counts:
                    continue  # Safety check.
                
                # Determine which time bucket the order falls into.
                hour = order_dt.hour
                bucket_index = None
                for idx, (start, end) in enumerate(bucket_boundaries):
                    if start <= hour < end:
                        bucket_index = idx
                        break
                if bucket_index is None:
                    continue  # Order time not in one of the defined buckets.
                
                # Increment the count by the order quantity.
                heat_counts[day_name][bucket_index] += order_item.quantity
        
        # Normalize the raw counts to a scale of 1 to 10.
        # Flatten the grid to get all counts.
        all_counts = [count for counts in heat_counts.values() for count in counts]
        min_count = min(all_counts)
        max_count = max(all_counts)
        
        if max_count == min_count:
            # If there is no variation (or no orders), use a constant score.
            constant_value = 1 if max_count == 0 else 5
            normalized_heat = { day: [constant_value] * 6 for day in days_of_week }
        else:
            normalized_heat = {}
            for day in days_of_week:
                normalized_heat[day] = []
                for count in heat_counts[day]:
                    # Map the count linearly: lowest becomes 1, highest becomes 10.
                    score = 1 + int((count - min_count) / (max_count - min_count) * 9)
                    normalized_heat[day].append(max(1, min(score, 10)))
        
        # Convert the normalized grid into D3 heatmap format:
        # an array of objects with keys: x (day), y (time bucket label), value (score)
        d3_data = []
        for day in days_of_week:
            for idx, score in enumerate(normalized_heat[day]):
                d3_data.append({
                    "x": day,
                    "y": bucket_labels[idx],
                    "value": score
                })
        season_d3_data[season] = d3_data
    
    return season_d3_data

