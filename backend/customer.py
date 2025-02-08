import random
import math
from segments import SEGMENTS

class Customer:
    def __init__(self, budget, price_sensitivity):
        self.budget = budget
        self.price_sensitivity = price_sensitivity

    def choose_items(self, items, combos, prices):
        """
        items: list of dict with keys [dish_id, baseline_utility, cost]
        combos: list of dict with keys [combo_name, baseline_utility, items, price]
        prices: dict {product_id: price}, product_id can be dish_id or combo_name

        Returns a dict {product_id: quantity} of purchased products.
        """
        choice_set = []
        for it in items:
            product_id = it["dish_id"]
            price = prices[product_id]
            # Utility is baseline utility + effect from price
            utility = it["baseline_utility"] + self.price_sensitivity * price
            choice_set.append((product_id, price, utility, 'item', [product_id]))

        for c in combos:
            product_id = c["combo_name"]
            price = prices[product_id]
            utility = c["baseline_utility"] + self.price_sensitivity * price
            choice_set.append((product_id, price, utility, 'combo', c["items"]))

        demands = {}
        for (pid, price, util, ptype, included_items) in choice_set:
            # Simple logistic function to determine purchase probability
            p_buy = 1.0 / (1.0 + math.exp(-util/2.0))

            quantity = 0
            if random.random() < p_buy and self.budget >= price:
                max_units = min(3, int(self.budget // price))
                if max_units > 0:
                    quantity = random.randint(1, max_units)
                    cost_total = quantity * price
                    if cost_total <= self.budget:
                        self.budget -= cost_total
                    else:
                        quantity = 1
                        self.budget -= price

            if quantity > 0:
                demands[pid] = demands.get(pid, 0) + quantity

        return demands

def create_customers():
    """
    Create a synthetic population of customers across different segments.
    """
    customers = []
    for seg in SEGMENTS:
        for _ in range(seg["count"]):
            budget = max(5, random.gauss(seg["budget_mean"], seg["budget_std"]))
            price_sensitivity = random.gauss(seg["price_sensitivity_mean"], seg["price_sensitivity_std"])
            customers.append(Customer(budget, price_sensitivity))
    return customers

def simulate(customers, menu_items, combos, prices):
    """
    Simulate purchasing behavior for a given price configuration.
    Returns:
      - total_profit: float
      - total_demand: dict {product_id -> quantity_sold}
      - customers_purchases: list of sets (each set is items the customer ended up with)
    """
    total_demand = {m["dish_id"]: 0 for m in menu_items}
    for c in combos:
        total_demand[c["combo_name"]] = 0
    total_profit = 0.0

    customers_purchases = []

    for cust in customers:
        cust_demands = cust.choose_items(menu_items, combos, prices)
        # Compute profit
        for pid, q in cust_demands.items():
            if pid in [m["dish_id"] for m in menu_items]:
                item_obj = next(x for x in menu_items if x["dish_id"] == pid)
                cost = item_obj["cost"]
                price = prices[pid]
                total_profit += (price - cost) * q
                total_demand[pid] += q
            else:
                # combo
                combo_obj = next(x for x in combos if x["combo_name"] == pid)
                price = prices[pid]
                combo_cost = 0.0
                for item_id in combo_obj["items"]:
                    it = next(x for x in menu_items if x["dish_id"] == item_id)
                    combo_cost += it["cost"]
                total_profit += (price - combo_cost) * q
                total_demand[pid] += q

        # Track which individual items the customer ends up buying for co-occurrence
        purchased_items = set()
        for pid, q in cust_demands.items():
            if pid in [m["dish_id"] for m in menu_items]:
                purchased_items.add(pid)
            else:
                combo_obj = next(x for x in combos if x["combo_name"] == pid)
                for cid in combo_obj["items"]:
                    purchased_items.add(cid)
        customers_purchases.append(purchased_items)

    return total_profit, total_demand, customers_purchases

def compute_elasticity(baseline_demand, new_demand, baseline_price, new_price):
    """
    Compute the price elasticity of demand for a product given:
      - baseline_demand, new_demand
      - baseline_price, new_price

    elasticity = ((Q2 - Q1)/Q1) / ((P2 - P1)/P1)
    If baseline demand is 0, we skip elasticity (return None).
    """
    if baseline_demand == 0 or baseline_price == 0:
        return None
    pct_change_demand = (new_demand - baseline_demand) / baseline_demand
    pct_change_price = (new_price - baseline_price) / baseline_price
    if pct_change_price == 0:
        return None
    return pct_change_demand / pct_change_price