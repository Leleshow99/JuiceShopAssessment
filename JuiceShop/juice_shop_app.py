import datetime as dt
import json
import uuid
from http import HTTPStatus

from flask import Flask, jsonify, make_response, request
from pony.flask import Pony

import JuiceShop.common as c
from JuiceShop.database import models, query

app = Flask(__name__)
Pony(app)

db = models.define_db(**c.DB_CONFIG)


def generate_uuid() -> str:
    return uuid.uuid4().hex[0:10]


def current_datetime() -> dt.datetime:
    return dt.datetime.utcnow()


@app.route(c.API_VERSION + '/fruits', methods=['GET'])
def list_fruits():
    """
    This function returns all fruits available. It combines the vitamins associated to each fruit.
    :return: json with all fruits stored in our DB with the associated vitamin.
    """
    response_dict = {'fruits': []}
    all_fruits = query.get_all_fruits(db)

    for fruit in all_fruits:
        fruit_vitamin = fruit.vitamins
        response_dict['fruits'].append({
            'name': fruit.name,
            'price': fruit.price / c.PRICE_DIVISOR,
            'description': fruit.description,
            'image': fruit.image,
            'vitamins': [
                {
                    'name': v.name,
                    'description': v.description,
                } for v in fruit_vitamin
            ]
        })

    return jsonify(response_dict)


@app.route(c.API_VERSION + '/liquids', methods=['GET'])
def list_liquids():
    """
    This function returns all liquids available.
    :return:
    """
    response_dict = {'liquids': []}
    all_liquids = query.get_all_liquids(db)

    for liquid in all_liquids:
        response_dict['liquids'].append({
            'name': liquid.name,
            'price': liquid.price / c.PRICE_DIVISOR,
            'description': liquid.description,
            'image': liquid.image
        })

    return jsonify(response_dict)


@app.route(c.API_VERSION + '/fruits/store', methods=['PUT'])
def store_new_fruit():
    """
    This endpoint is used to store / update fruits to database.
    :return: a JSON with the created or updated fruit
    """
    received_fruit = json.loads(request.data)

    new_fruit = query.get_fruit_by_name(db, received_fruit['name'].lower())
    if new_fruit is None:
        new_fruit = db.Fruit(name=received_fruit['name'],
                             price=int(received_fruit['price'] * c.PRICE_DIVISOR),
                             description=received_fruit['description'],
                             image=received_fruit['image']
                             )
    else:
        new_fruit(name=received_fruit['name'],
                  price=int(received_fruit['price'] * c.PRICE_DIVISOR),
                  description=received_fruit['description'],
                  image=received_fruit['image']
                  )

    for vit_name in received_fruit['vitamins']:
        vitamin = query.get_vitamin_by_name(db, vit_name)
        if vitamin is None:
            continue
        new_fruit.vitamins.add(vitamin)

    return jsonify(c.fruit_to_dict(new_fruit))


@app.route(c.API_VERSION + '/liquids/store', methods=['PUT'])
def store_new_liquid():
    """
    This endpoint is used to store new liquids to database.
    :return: a JSON with the created liquid, or HTTP 409 when liquids name already exists.
    """
    received_liquid = json.loads(request.data)

    new_liquid = query.get_liquid_by_name(db, received_liquid['name'].lower())
    if new_liquid is None:
        new_liquid = db.Fruit(name=received_liquid['name'],
                              price=int(received_liquid['price'] * c.PRICE_DIVISOR),
                              description=received_liquid['description'],
                              image=received_liquid['image']
                              )
    else:
        new_liquid(name=received_liquid['name'],
                   price=int(received_liquid['price'] * c.PRICE_DIVISOR),
                   description=received_liquid['description'],
                   image=received_liquid['image']
                   )

    return jsonify(c.liquid_to_dict(new_liquid))


@app.route(c.API_VERSION + '/juices', methods=['GET'])
def get_juices():
    """
    This endpoint returns all the juices ordered. The shop owner can use this endpoint for further analyses.
    :return: a JSON with all juices ordered.
    """
    response_dict = {'juices': []}

    all_juices = query.get_all_juices(db)
    for juice in all_juices:
        response_dict['juices'].append({
            'id': juice.id,
            'price': juice.price / c.PRICE_DIVISOR,
            'fruits': [
                {
                    'name': f.name,
                    'price': f.price / c.PRICE_DIVISOR,
                } for f in juice.fruits
            ],
            'liquid': {
                'name': juice.liquid.name,
                'price': juice.liquid.price / c.PRICE_DIVISOR
            },
            'order_datetime': juice.order.order_at,
            'order_total': juice.order.price / c.PRICE_DIVISOR
        })

    return jsonify(response_dict)


@app.route(c.API_VERSION + '/order', methods=['POST'])
def receive_order():
    """
    This endpoint receives a JSON with an order. The order should contain a list of Juices. The order cost is calculated
    and returned a payment id and the order details.
    :return: A JSON with the order created and the payment id.
    """
    received_order = json.loads(request.data)
    new_order = db.Order(
        payment_id=generate_uuid(),
        order_at=current_datetime(),
        is_paid=False
    )

    order_price = 0
    for juice in received_order['order']:
        juice_price = 0
        new_juice = db.Juice()
        for fruit_name in juice['fruits']:
            fruit = query.get_fruit_by_name(db, fruit_name)
            if fruit is None:
                continue
            new_juice.fruits.add(fruit)
            juice_price += fruit.price
        liquid = query.get_liquid_by_name(db, juice['liquid'])
        if liquid is None:
            continue
        new_juice.liquid = liquid
        juice_price += liquid.price
        new_juice.price = juice_price
        new_juice.order = new_order
        order_price += juice_price
    new_order.price = order_price

    return jsonify(c.order_to_dict(new_order))


@app.route(c.API_VERSION + '/order/<string:payment_id>', methods=['PUT', 'GET'])
def update_payment_status(payment_id):
    """
    This endpoint is used to update and retrieve an order payment status.
    :return: a JSON with the payment status. If the order doesn't exist, it returns an HTTP Error 404.
    """
    if request.method == 'PUT':
        received_payment = json.loads(request.data)
        order_to_update = query.get_order_by_payment_id(db, payment_id)
        if order_to_update is None:
            response = make_response('Resource not found', HTTPStatus.NOT_FOUND)
            return response
        order_to_update.is_paid = received_payment['is_paid']
        return jsonify(c.order_to_dict(order_to_update))

    requested_order = db.Order.get(payment_id=payment_id)
    if requested_order is None:
        response = make_response('Resource not found', HTTPStatus.NOT_FOUND)
        return response

    return jsonify(c.order_to_dict(requested_order))


@app.route(c.API_VERSION + '/juice/description', methods=['POST'])
def get_juice_description():
    """
    This endpoint returns a JSON with the description of each ingredient of a juice. The description also gives a
    list of the Vitamins and its benefits.
    :return: JSON with a description of a juice ingredients and benefits.
    """
    juice_ingredients = json.loads(request.data)
    juice_descr = {
        'fruits': [],
        'vitamins': [],
        'liquid': {}
    }

    for fruit_name in juice_ingredients['fruits']:
        fruit = query.get_fruit_by_name(db, fruit_name)
        juice_descr['fruits'].append({
            'name': fruit.name,
            'description': fruit.description
        })
        for vitamin in fruit.vitamins:
            juice_descr['vitamins'].append({
                'name': vitamin.name,
                'description': vitamin.description
            })
    juice_liquid = query.get_liquid_by_name(db, juice_ingredients['liquid'])
    juice_descr['liquid'] = {
        'name': juice_liquid.name,
        'description': juice_liquid.description
    }

    return jsonify(juice_descr)
