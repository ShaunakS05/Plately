from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MenuItem(BaseModel):
    dish_id: str
    name: str
    price: float
    cost: float
    quantity_sold: int
    portion_size: int
    baseline_utility: Optional[float] = None

class Combo(BaseModel):
    combo_name: str
    items: List[str]
    price: float
    quantity_sold: int
    baseline_utility: Optional[float] = None

class OrderItem(BaseModel):
    dish_id: str
    quantity: int
    special_instructions: Optional[str] = None

class OrderCombo(BaseModel):
    combo_name: str
    quantity: int

class Order(BaseModel):
    order_id: str
    dining_option: str  # dine-in, takeout, delivery
    items: List[OrderItem]
    combos: Optional[List[OrderCombo]] = None
    guest_name: Optional[str] = None
    delivery_address: Optional[str] = None
    order_timestamp: Optional[str] = None
    season: Optional[str] = None
    day: Optional[str] = None