"""Develop a backend API for managing a pizza ordering system

Start with the first task and move to the next task only after the previous one is implemented and tested. 

Fetch Menu items:
Given the name of a pizza return its details
/menu?name=”name-of-pizza”

Example: GET /menu?name=margherita will return 

{"id": 1, "name": "Margherita", "size": "Medium", "price": 8.99, "toppings": ["tomato sauce", "mozzarella", "basil"]}

Order Management:
Place an order for pizzas using /order endpoint and return total final price and an order id

Example: POST /order will return
Request Body: [{ 'id': 1, 'quantity': 2 }, { 'id': 3, 'quantity': 5 }]
Response: {'order_id': 12345, 'price': 67.93 }




Mock Data



"""

pizza_menu = [
    {
        "id": 1,
        "name": "Margherita",
        "size": "Medium",
        "price": 8.99,
        "toppings": ["tomato sauce", "mozzarella", "basil"],
    },
    {
        "id": 2,
        "name": "Pepperoni",
        "size": "Medium",
        "price": 9.99,
        "toppings": ["tomato sauce", "mozzarella", "pepperoni"],
    },
    {
        "id": 3,
        "name": "Vegetarian",
        "size": "Medium",
        "price": 10.99,
        "toppings": [
            "tomato sauce",
            "mozzarella",
            "bell peppers",
            "onions",
            "mushrooms",
        ],
    },
    {
        "id": 4,
        "name": "Hawaiian",
        "size": "Medium",
        "price": 11.99,
        "toppings": ["tomato sauce", "mozzarella", "ham", "pineapple"],
    },
    {
        "id": 5,
        "name": "BBQ Chicken",
        "size": "Medium",
        "price": 12.99,
        "toppings": ["BBQ sauce", "mozzarella", "grilled chicken", "red onions"],
    },
    {
        "id": 6,
        "name": "Cheese",
        "size": "Medium",
        "price": 9.99,
        "toppings": ["tomato sauce", "mozzarella"],
    },
    {
        "id": 7,
        "name": "Mushroom",
        "size": "Medium",
        "price": 10.99,
        "toppings": ["tomato sauce", "mozzarella", "mushrooms"],
    },
    {
        "id": 8,
        "name": "Spinach and Feta",
        "size": "Medium",
        "price": 11.99,
        "toppings": ["tomato sauce", "mozzarella", "spinach", "feta cheese"],
    },
    {
        "id": 9,
        "name": "Meat Lover's",
        "size": "Medium",
        "price": 12.99,
        "toppings": [
            "tomato sauce",
            "mozzarella",
            "pepperoni",
            "sausage",
            "ham",
            "bacon",
        ],
    },
    {
        "id": 10,
        "name": "Buffalo Chicken",
        "size": "Medium",
        "price": 13.99,
        "toppings": [
            "Buffalo sauce",
            "mozzarella",
            "grilled chicken",
            "red onions",
            "blue cheese",
        ],
    },
]

from pydantic import BaseModel

from fastapi import FastAPI
import ast

app = FastAPI()


class OrderItem(BaseModel):
    id: int
    quantity: int


@app.get("/menu")
async def fetch_menu(name: str):
    for item in pizza_menu:
        if item["name"].lower() == name:
            return item


@app.post("/order")
async def create_order(order_items: list[OrderItem]):
    total_price = 0
    unique_id = 12345
    print(order_items)
    for item in order_items:
        order_id = item.id
        quantity = item.quantity
        for menu_item in pizza_menu:
            if menu_item["id"] == order_id:
                total_price += quantity * menu_item["price"]

    return {"order_id": unique_id, "price": total_price}
