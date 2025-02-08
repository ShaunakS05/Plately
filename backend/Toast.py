from MenuClasses import MenuItem, Combo, OrderItem, OrderCombo, Order
from datetime import datetime, timedelta
import random


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

# Generate fake orders
def generate_fake_orders(menu_items, combos):
    orders = []
    now = datetime.now()

    for _ in range(random.randint(25, 50)):
        # Generate a random timestamp within the last 30 days
        random_offset = random.randint(0, 30 * 24 * 60 * 60)  # Up to 30 days in the past
        order_time = now - timedelta(seconds=random_offset)

        order_items = [
            OrderItem(
                dish_id=item.dish_id,
                quantity=random.randint(1, 4),
                special_instructions=random.choice([None, "Extra spicy", "No peanuts", "Gluten-free"]),
            )
            for item in random.sample(menu_items, random.randint(1, 5))
        ]

        order_combos = [
            OrderCombo(
                combo_name=combo.combo_name,
                quantity=random.randint(1, 2),
            )
            for combo in random.sample(combos, random.randint(0, len(combos)))
        ]

        order = Order(
            order_id=f"ORDER{random.randint(10000, 99999)}",
            dining_option=random.choice(["dine-in", "takeout", "delivery"]),
            items=order_items,
            combos=order_combos if order_combos else None,
            guest_name=random.choice(["John Doe", "Jane Smith", "Alex Johnson", "Wei Zhang", "Ling Chen"]),
            delivery_address=random.choice(["123 Main St", "456 Elm St", "789 Maple Ave", None]),
            order_timestamp=order_time.isoformat(),  # ✅ Minimal change: Add timestamp
        )
        orders.append(order)

    return orders