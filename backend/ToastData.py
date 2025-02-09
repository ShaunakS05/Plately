from MenuClasses import MenuItem, Combo, OrderItem, OrderCombo, Order
from datetime import datetime, timedelta
import random, requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

menu_categories = {
    "Appetizers": [
        ("Spring Rolls", 5.00, 2.50, 120),
        ("Crab Rangoon", 6.50, 3.00, 110),
        ("Fried Dumplings", 7.00, 3.50, 130),
        ("Edamame", 4.50, 2.00, 80),
        ("Chicken Satay", 6.00, 3.00, 90),
    ],
    "Entrees": [
        ("Kung Pao Chicken", 12.00, 6.00, 140),
        ("Mongolian Beef", 13.50, 7.00, 120),
        ("Shrimp with Broccoli", 14.00, 7.50, 100),
        ("Vegetable Stir-Fry", 10.00, 5.00, 90),
        ("Orange Chicken", 11.50, 6.00, 130),
        ("Sesame Tofu", 11.00, 5.50, 100),
        ("Beef Chow Fun", 13.00, 6.50, 110),
        ("Honey Walnut Shrimp", 15.00, 8.00, 80),
    ],
    "Soups": [
        ("Hot and Sour Soup", 4.50, 1.50, 150),
        ("Egg Drop Soup", 4.00, 1.20, 160),
        ("Chicken Corn Soup", 5.50, 2.00, 90),
    ],
    "Desserts": [
        ("Fried Ice Cream", 6.00, 3.00, 60),
        ("Sesame Balls", 5.00, 2.50, 70),
        ("Mango Pudding", 5.50, 2.80, 50),
    ],
    "Drinks": [
        ("Green Tea", 2.50, 0.80, 200),
        ("Bubble Tea", 4.50, 2.50, 100),
        ("Soda", 2.00, 0.50, 250),
    ],
}

def generate_fake_menu():
    menu_items = []
    for category, items in menu_categories.items():
        for idx, (name, price, cost, quantity_sold) in enumerate(items):
            dish_id = f"{category[:2].upper()}{idx + 1:03}"
            menu_items.append(
                MenuItem(
                    dish_id=dish_id,
                    name=name,
                    price=price,
                    cost=cost,
                    quantity_sold=random.randint(quantity_sold - 20, quantity_sold + 20),
                    portion_size=random.randint(150, 400),
                )
            )
    return menu_items

# Create realistic combos
def generate_fake_combos(menu_items):
    return [
        Combo(combo_name="Appetizer + Entree", items=[menu_items[0].dish_id, menu_items[5].dish_id], price=15.00, quantity_sold=random.randint(40, 80)),
        Combo(combo_name="Soup + Entree", items=[menu_items[10].dish_id, menu_items[6].dish_id], price=16.00, quantity_sold=random.randint(50, 70)),
        Combo(combo_name="Family Special", items=[menu_items[2].dish_id, menu_items[4].dish_id, menu_items[9].dish_id], price=30.00, quantity_sold=random.randint(30, 60)),
    ]

SEASONS = { 
    "Winter": [12,1,2],
    "Spring": [3,4,5],
    "Summer": [6,7,8],
    "Fall": [9,10,11]
}

def get_season(month):
    for season, months in SEASONS.items():
        if month in months:
            return season
    return "Unkown"

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
        order_season = get_season(order_time.month)
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
            season=order_season,
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
        return generate_fake_menu()

def fetch_combos():
    try:
        response = requests.get(f"{TOAST_API_BASE_URL}/combos", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning("Failed to fetch combos from Toast API (%s). Using local fake combos data.", e)
        # If generate_fake_combos needs menu_items, you might call fetch_menu_items() first.
        return generate_fake_combos(fetch_menu_items())

