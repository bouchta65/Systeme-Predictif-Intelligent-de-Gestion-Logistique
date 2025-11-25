from fastapi import FastAPI, WebSocket
import random, json, asyncio
from datetime import datetime

app = FastAPI()

ORDER_COUNTRIES = ["USA", "Mexico", "Brazil", "France", "Germany", "UK", "China", "India"]
TYPES = ["DEBIT", "TRANSFER", "PAYMENT", "CASH"]
ORDER_REGIONS = ["Western US", "Central US", "Southern US", "Eastern US", "Southeast Asia", "Central America", "South America", "Western Europe", "Central Europe"]
SHIPPING_MODES = ["Standard Class", "First Class", "Second Class", "Same Day"]
DEPARTMENT_NAMES = ["Fitness", "Apparel", "Golf", "Outdoors", "Fan Shop", "Footwear", "Technology"]
CATEGORY_NAMES = ["Sporting Goods", "Cleats", "Women's Apparel", "Men's Footwear", "Cameras", "Computers", "Electronics"]

@app.get("/")
def root():
    return {"message": "API is running"}

def generate_random_order():
    qty = random.randint(1, 5)
    price = round(random.uniform(10, 500), 2)
    discount = round(random.uniform(0, 50), 2)
    total = round(price * qty - discount, 2)
    profit = round(total * random.uniform(0.1, 0.4), 2)
    
    return {
        "Benefit per order": profit, "Sales per customer": round(random.uniform(50, 1000), 2),
        "Order Item Quantity": qty, "Order Item Product Price": price, "Order Item Discount": discount,
        "Order Item Total": total, "Order Profit Per Order": profit, "distance": round(random.uniform(10, 20000), 2),
        "Late_delivery_risk": random.choice([0, 1]), "Order Country": random.choice(ORDER_COUNTRIES),
        "Type": random.choice(TYPES), "Order Region": random.choice(ORDER_REGIONS),
        "Shipping Mode": random.choice(SHIPPING_MODES), "Department Name": random.choice(DEPARTMENT_NAMES),
        "Category Name": random.choice(CATEGORY_NAMES), "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws/orders")
async def websocket_orders(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_text(json.dumps(generate_random_order()))
            await asyncio.sleep(1)
    except:
        pass
