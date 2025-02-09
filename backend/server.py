from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import openai
import requests
from customer import create_customers, compute_elasticity
from customer import simulate
import random
import itertools
import logging
from ToastData import generate_fake_combos, generate_fake_menu, generate_fake_orders, fetch_menu_items, fetch_combos, calculate_heat_scores_d3
from MenuClasses import Order
import time, asyncio, requests, logging
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder






logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOAST_API_BASE_URL = "http://127.0.0.1:8001"
@asynccontextmanager
async def lifespan(app: FastAPI):
    timeout_seconds = 10
    start_time = time.time()
    while True:
        try:
            response = requests.get(f"{TOAST_API_BASE_URL}/menu", timeout=3)
            response.raise_for_status()
            logger.info("Toast API endpoint is running")
            break
        except Exception as e:
            logger.warning("Toast API endpoint not reachable yet, retrying... (%s)", e)
        if time.time() - start_time > timeout_seconds:
            logger.error("Failed to connect to Toast API endpoint after %s seconds.", timeout_seconds)
            break
        await asyncio.sleep(1)
    
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = ""


menu_items = generate_fake_menu()
combos = generate_fake_combos(menu_items)
orders = generate_fake_orders(menu_items, combos)

@app.get("/")
def root():
    return {"message": "Hello World"}

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
        menu_items = fetch_menu_items()
        combos = fetch_combos()

        # We won't directly use orders here but ensure they exist
        # orders_resp = requests.get(f"{TOAST_API_BASE_URL}/orders")
        # orders_resp.raise_for_status()

        # --- 2) Compute baseline utilities ---
        item_sales = np.array([m.quantity_sold for m in menu_items])
        item_baseline_util = np.log(item_sales + 1)
        item_baseline_util = item_baseline_util - np.mean(item_baseline_util)

        for i, m in enumerate(menu_items):
            m.baseline_utility = item_baseline_util[i]

        # Combos baseline utilities
        if len(combos) > 0:
            combo_sales = np.array([c.quantity_sold for c in combos])
            combo_baseline_util = np.log(combo_sales + 1)
            combo_baseline_util = combo_baseline_util - np.mean(combo_baseline_util)
            for i, c in enumerate(combos):
                c.baseline_utility = combo_baseline_util[i]
        else:
            for c in combos:
                c.baseline_utility = 0.0

        # --- 3) Perform a random search to find optimal prices ---
        base_item_prices = {m.dish_id: m.price for m in menu_items}
        base_combo_prices = {c.combo_name: c.price for c in combos}
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

        dish_ids = [m.dish_id for m in menu_items]
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
            pid = m.dish_id
            curr_price = m.price
            opt_price = best_prices[pid]
            demand = final_demand[pid] if pid in final_demand else 0
            profit = (opt_price - m.cost) * demand

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
                f"Item {m.name} (ID: {pid}) changed from ${curr_price:.2f} to ${opt_price:.2f}. "
                f"Demand changed from {base_q} to {new_q}, leading to an elasticity of {elasticity}. "
                f"This indicates {elasticity_label}. "
                f"Profit impact: ${profit:.2f}."
            )

            explanation_details.append(reason_snippet)

            results.append({
                "dish_id": pid,
                "dish_name": m.name,
                "current_price": round(curr_price, 2),
                "optimal_price": round(opt_price, 2),
                "expected_profit": round(profit, 2),
                "expected_demand": int(demand),
                "elasticity": elasticity if elasticity else None
            })

        # Summarize co-occurrence pattern
        if best_pair is not None:
            itemA = next(x for x in menu_items if x.dish_id == best_pair[0])
            itemB = next(x for x in menu_items if x.dish_id == best_pair[1])
            pair_info = f"The items '{itemA.name}' and '{itemB.name}' (IDs: {itemA.dish_id}, {itemB.dish_id}) are frequently purchased together (co-occurrence count: {max_co})."
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
        item_sales = np.array([m.quantity_sold for m in menu_items])
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
    

@app.get("/menu")
def get_menu():
    return menu_items

@app.get("/combos")
def get_combos():
    return combos

@app.get("/orders")
def get_orders():
    """
    Return the 50 fake orders.
    """
    return JSONResponse(content=jsonable_encoder(orders))

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

@app.get("/order-timestamps", tags=["Orders"])
def get_order_timestamps():
    return {"timestamps": [order.order_timestamp for order in orders if order.order_timestamp]}

@app.get("/orders/season/{season}", tags=["Orders"])
def get_orders_by_season(season: str):
    season = season.capitalize()
    filtered_orders = [order for order in orders if order.season == season]
    if not filtered_orders:
        raise HTTPException(status_code=404, detail=f"No orders found for season: {season}")
    return {"season": season, "orders": filtered_orders}

@app.get("/orders/day/{day}", tags=["Orders"])
def get_orders_by_day(day: str):
    day = day.capitalize()
    filtered_orders = [order for order in orders if order.day == day]
    if not filtered_orders:
        raise HTTPException(status_code=404, detail=f"No orders found for day: {day}")
    return {"day": day, "orders": filtered_orders}

@app.get("/heatscores/{menu_item_id}")
def get_heatscores(menu_item_id: str):
    data = calculate_heat_scores_d3(menu_item_id, orders)
    return JSONResponse(content=data)
