from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    print("Restaurants found:", restaurants)

    restaurants_list = []
    for restaurant in restaurants:
        restaurant_dict = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name
        }
        restaurants_list.append(restaurant_dict)
    return make_response(jsonify(restaurants_list), 200)

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        response_body = {'error': 'Restaurant not found'}
        return make_response(jsonify(response_body), 404)

    restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
    pizzas_list = []

    for rpizza in restaurant_pizzas:
        pizza = Pizza.query.get(rpizza.pizza_id)
        pizza_data = {
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name
        }
        rpizza_data = {
            "id": rpizza.id,
            "pizza": pizza_data,
            "pizza_id": rpizza.pizza_id,
            "price": rpizza.price,
            "restaurant_id": rpizza.restaurant_id
        }
        pizzas_list.append(rpizza_data)

    response_body = {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": pizzas_list
    }
    return make_response(jsonify(response_body), 200)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        response_body = {"error": "Restaurant not found"}
        return make_response(jsonify(response_body), 404)

    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    print("Pizzas found:", pizzas)

    if not pizzas:
        return jsonify({"message": "No pizzas found"}), 404

    pizzas_list = []
    for pizza in pizzas:
        pizza_dict = {
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name
        }
        pizzas_list.append(pizza_dict)
    return make_response(jsonify(pizzas_list), 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def handle_rpizza():
    data = request.json
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if price is None or pizza_id is None or restaurant_id is None:
        response_body = {"error": "Invalid input"}
        return make_response(jsonify(response_body), 400)

    price = int(price)
    pizza_id = int(pizza_id)
    restaurant_id = int(restaurant_id)

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza or not restaurant:
        response_body = {"error": "Pizza or Restaurant not found"}
        return make_response(jsonify(response_body), 404)

    new_rpizza = RestaurantPizza(
        price=price,
        pizza_id=pizza_id,
        restaurant_id=restaurant_id
    )
    
    try:
        db.session.add(new_rpizza)
        db.session.commit()
    except ValueError as e:
        response_body = {"error": str(e)}
        return make_response(jsonify(response_body), 400)

    response_body = {
        "id": new_rpizza.id,
        "pizza": {
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name
        },
        "pizza_id": new_rpizza.pizza_id,
        "price": new_rpizza.price,
        "restaurant": {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name
        },
        "restaurant_id": new_rpizza.restaurant_id
    }
    return make_response(jsonify(response_body), 201)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
    
    
    
    
    
    
    
    
    