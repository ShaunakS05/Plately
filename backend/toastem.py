from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
import numpy as np
import random
import math
import openai
import itertools

app = FastAPI()

# Enable CORS (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOAST_API_BASE_URL = "http://127.0.0.1:8001"

# Set your OpenAI API key (Replace with a secure method in production)
openai.api_key = "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"
# Customer segments parameters
SEGMENTS = [
    {
        "name": "frequent",
        "count": 100,
        "budget_mean": 80,
        "budget_std": 20,
        "price_sensitivity_mean": -0.04,
        "price_sensitivity_std": 0.01,
    },
    {
        "name": "occasional",
        "count": 80,
        "budget_mean": 50,
        "budget_std": 15,
        "price_sensitivity_mean": -0.06,
        "price_sensitivity_std": 0.01,
    },
    {
        "name": "rare",
        "count": 60,
        "budget_mean": 30,
        "budget_std": 10,
        "price_sensitivity_mean": -0.08,
        "price_sensitivity_std": 0.02,
    },
]

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

@app.post("/optimize-prices")
def optimize_prices():
    """
    This endpoint:
      1) Fetches menu items and combos
      2) Estimates baseline utilities
      3) Performs a random search to find an optimal price configuration
      4) Computes final profit and demand
      5) Uses GPT to generate a textual explanation of the changes
      6) Returns the numeric results plus total expected profit
    """
    try:
        # --- 1) Fetch data ---
        menu_resp = requests.get(f"{TOAST_API_BASE_URL}/menu")
        menu_resp.raise_for_status()
        menu_items = menu_resp.json()

        combos_resp = requests.get(f"{TOAST_API_BASE_URL}/combos")
        combos_resp.raise_for_status()
        combos = combos_resp.json()

        # We won't directly use orders here but ensure they exist
        orders_resp = requests.get(f"{TOAST_API_BASE_URL}/orders")
        orders_resp.raise_for_status()

        # --- 2) Compute baseline utilities ---
        item_sales = np.array([m["quantity_sold"] for m in menu_items])
        item_baseline_util = np.log(item_sales + 1)
        item_baseline_util = item_baseline_util - np.mean(item_baseline_util)

        for i, m in enumerate(menu_items):
            m["baseline_utility"] = item_baseline_util[i]

        # Combos baseline utilities
        if len(combos) > 0:
            combo_sales = np.array([c["quantity_sold"] for c in combos])
            combo_baseline_util = np.log(combo_sales + 1)
            combo_baseline_util = combo_baseline_util - np.mean(combo_baseline_util)
            for i, c in enumerate(combos):
                c["baseline_utility"] = combo_baseline_util[i]
        else:
            for c in combos:
                c["baseline_utility"] = 0.0

        # --- 3) Perform a random search to find optimal prices ---
        base_item_prices = {m["dish_id"]: m["price"] for m in menu_items}
        base_combo_prices = {c["combo_name"]: c["price"] for c in combos}
        base_prices = {**base_item_prices, **base_combo_prices}

        # We'll do a baseline simulation to compare
        baseline_customers = create_customers()
        baseline_profit, baseline_demand, _ = simulate(baseline_customers, menu_items, combos, base_prices)

        N = 50  # Number of random trials
        best_profit = -np.inf
        best_prices = None
        best_demands = None

        for _ in range(N):
            trial_prices = {}
            for pid in base_prices:
                multiplier = random.uniform(0.7, 1.3)
                trial_prices[pid] = base_prices[pid] * multiplier

            # Fresh set of customers for each simulation
            trial_customers = create_customers()
            total_profit, total_demand, _ = simulate(trial_customers, menu_items, combos, trial_prices)
            if total_profit > best_profit:
                best_profit = total_profit
                best_prices = trial_prices
                best_demands = total_demand

        if best_prices is None:
            raise HTTPException(status_code=500, detail="No optimal price found")

        # --- 4) Final simulation & co-occurrence analysis with best prices ---
        final_customers = create_customers()
        final_profit, final_demand, customers_purchases = simulate(final_customers, menu_items, combos, best_prices)

        dish_ids = [m["dish_id"] for m in menu_items]
        dish_index = {d: i for i, d in enumerate(dish_ids)}
        co_occurrence = np.zeros((len(dish_ids), len(dish_ids)))

        for purchase_set in customers_purchases:
            for a, b in itertools.combinations(purchase_set, 2):
                i, j = dish_index[a], dish_index[b]
                co_occurrence[i, j] += 1
                co_occurrence[j, i] += 1

        max_co = -1
        best_pair = None
        for i in range(len(dish_ids)):
            for j in range(i+1, len(dish_ids)):
                if co_occurrence[i,j] > max_co:
                    max_co = co_occurrence[i,j]
                    best_pair = (dish_ids[i], dish_ids[j])

        # --- 5) Prepare results and compute elasticity for explanations ---
        results = []
        explanation_details = []

        for m in menu_items:
            pid = m["dish_id"]
            curr_price = m["price"]
            opt_price = best_prices[pid]
            demand = final_demand[pid] if pid in final_demand else 0
            profit = (opt_price - m["cost"]) * demand

            # Compute elasticity from baseline scenario
            base_q = baseline_demand.get(pid, 0)
            new_q = demand
            base_p = curr_price
            new_p = opt_price
            elasticity = compute_elasticity(base_q, new_q, base_p, new_p)

            # Simple label for elasticity
            elasticity_label = ""
            if elasticity is not None:
                if abs(elasticity) < 1:
                    elasticity_label = "Inelastic demand"
                else:
                    elasticity_label = "Elastic demand"
            else:
                elasticity_label = "Not enough data / N/A"

            # Build explanation snippet for each item
            reason_snippet = (
                f"Item {m['name']} (ID: {pid}) changed from ${curr_price:.2f} to ${opt_price:.2f}. "
                f"Demand changed from {base_q} to {new_q}, leading to an elasticity of {elasticity}. "
                f"This indicates {elasticity_label}. "
                f"Profit impact: ${profit:.2f}."
            )

            explanation_details.append(reason_snippet)

            results.append({
                "dish_id": pid,
                "dish_name": m["name"],
                "current_price": round(curr_price, 2),
                "optimal_price": round(opt_price, 2),
                "expected_profit": round(profit, 2),
                "expected_demand": int(demand),
                "elasticity": elasticity if elasticity else None
            })

        # Summarize co-occurrence pattern
        if best_pair is not None:
            itemA = next(x for x in menu_items if x["dish_id"] == best_pair[0])
            itemB = next(x for x in menu_items if x["dish_id"] == best_pair[1])
            pair_info = f"The items '{itemA['name']}' and '{itemB['name']}' (IDs: {itemA['dish_id']}, {itemB['dish_id']}) are frequently purchased together (co-occurrence count: {max_co})."
        else:
            pair_info = "No significant co-occurrence patterns were found."

        # Prepare prompt for OpenAI
        # We incorporate some of the economics language and rationale from the random search approach.
        prompt = f"""
You are an expert restaurant data analyst. We have just optimized our menu item prices using a combination of
marginal analysis and random search. Below are key facts:
- Baseline profit before optimization: ${baseline_profit:.2f}
- Best found profit after optimization: ${final_profit:.2f}
- {pair_info}
- Detailed item-by-item changes:
{chr(10).join(explanation_details)}

Explain to a restaurant manager (in simple terms) why these changes were made, focusing on:
1) Price elasticity of demand and how it influenced higher or lower prices.
2) The potential for creating a combo with high co-occurrence items.
3) How these adjustments lead to an improvement in overall profit.
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are ChatGPT, a helpful AI assistant for restaurant analytics."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7,
        )

        explanation_text = response.choices[0].message['content']

        return {
            "baseline_profit": round(baseline_profit, 2),
            "optimized_profit": round(final_profit, 2),
            "results": results,
            "co_occurrence_info": pair_info,
            "ai_explanation": explanation_text
        }

    except Exception as e:
        logger.exception("Unexpected Error")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.post("/scenario-analysis")
def scenario_analysis(
    custom_price_factors: dict = Body(
        ...,
        example={
            "Burger": 1.1,   # 10% increase
            "Pizza": 0.9,    # 10% decrease
            "Combo A": 1.05  # 5% increase
        }
    )
):
    """
    This endpoint allows you to pass a dictionary of {dish_id or combo_name: multiplier}.
    It will simulate the outcome of those price changes and return profit/demand.
    Example body:
      {
         "Burger": 1.1,
         "Pizza": 0.9,
         "Combo A": 1.05
      }
    """
    try:
        # --- Fetch menu and combos ---
        menu_resp = requests.get(f"{TOAST_API_BASE_URL}/menu")
        menu_resp.raise_for_status()
        menu_items = menu_resp.json()

        combos_resp = requests.get(f"{TOAST_API_BASE_URL}/combos")
        combos_resp.raise_for_status()
        combos = combos_resp.json()

        # Compute baseline utilities
        item_sales = np.array([m["quantity_sold"] for m in menu_items])
        item_baseline_util = np.log(item_sales + 1)
        item_baseline_util = item_baseline_util - np.mean(item_baseline_util)
        for i, m in enumerate(menu_items):
            m["baseline_utility"] = item_baseline_util[i]

        if len(combos) > 0:
            combo_sales = np.array([c["quantity_sold"] for c in combos])
            combo_baseline_util = np.log(combo_sales + 1)
            combo_baseline_util = combo_baseline_util - np.mean(combo_baseline_util)
            for i, c in enumerate(combos):
                c["baseline_utility"] = combo_baseline_util[i]
        else:
            for c in combos:
                c["baseline_utility"] = 0.0

        # Base prices
        base_item_prices = {m["dish_id"]: m["price"] for m in menu_items}
        base_combo_prices = {c["combo_name"]: c["price"] for c in combos}
        base_prices = {**base_item_prices, **base_combo_prices}

        # Apply multipliers
        scenario_prices = {}
        for pid, base_price in base_prices.items():
            if pid in custom_price_factors:
                scenario_prices[pid] = base_price * custom_price_factors[pid]
            else:
                scenario_prices[pid] = base_price

        # --- Simulate scenario ---
        scenario_customers = create_customers()
        total_profit, total_demand, _ = simulate(scenario_customers, menu_items, combos, scenario_prices)

        # Return numeric results
        scenario_result = []
        for m in menu_items:
            pid = m["dish_id"]
            price = scenario_prices[pid]
            scenario_result.append({
                "dish_id": pid,
                "scenario_price": round(price, 2),
                "demand": total_demand[pid],
                "revenue": round(price * total_demand[pid], 2)
            })
        for c in combos:
            pid = c["combo_name"]
            price = scenario_prices[pid]
            scenario_result.append({
                "combo_name": pid,
                "scenario_price": round(price, 2),
                "demand": total_demand[pid],
                "revenue": round(price * total_demand[pid], 2)
            })

        return {
            "scenario_profit": round(total_profit, 2),
            "scenario_details": scenario_result
        }

    except Exception as e:
        logger.exception("Unexpected Error in scenario_analysis")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


from fastapi import FastAPI, HTTPException
import random
from fastapi.middleware.cors import CORSMiddleware
from Toast import generate_fake_combos, generate_fake_menu, generate_fake_orders
from MenuClasses import Order

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins like ["http://localhost:3000"] for stricter policies
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Define models for the Toast API


# Create an expanded realistic menu


menu_items = generate_fake_menu()
combos = generate_fake_combos(menu_items)
orders = generate_fake_orders(menu_items, combos)

# API Endpoints
@app.get("/menu")
def get_menu():
    return menu_items

@app.get("/combos")
def get_combos():
    return combos

@app.get("/orders")
def get_orders():
    return orders

@app.get("/orders/{order_id}")
def get_order_by_id(order_id: str):
    for order in orders:
        if order.order_id == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")

@app.post("/orders")
def create_order(order: Order):
    orders.append(order)
    return {"message": "Order created successfully", "order_id": order.order_id}

# Run the emulator
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)