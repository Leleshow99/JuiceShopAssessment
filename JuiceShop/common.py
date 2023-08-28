from pony.orm import db_session

DB_FILE = 'juice_shop_db'
PRICE_DIVISOR = 100
API_VERSION = '/v1'

DB_CONFIG = dict(provider='sqlite', filename=DB_FILE, create_db=True)


@db_session
def order_to_dict(order_object) -> dict:
    """
    This function creates a dict using an order object as reference.
    :param order_object: the order object to be converted to dict.
    :return: a dict with order data
    """
    order_dict = {
        'price': order_object.price / PRICE_DIVISOR,
        'order_at': order_object.order_at,
        'is_paid': order_object.is_paid,
        'payment_id': order_object.payment_id,
        'juices': []
    }

    for juice in order_object.juices:
        order_dict['juices'].append(
            {
                'price': juice.price / PRICE_DIVISOR,
                'liquid': {'name': juice.liquid.name, 'price': juice.liquid.price / PRICE_DIVISOR},
                'fruits': [{'name': f.name, 'price': f.price / PRICE_DIVISOR} for f in juice.fruits]
            }
        )

    return order_dict


@db_session
def fruit_to_dict(fruit_object) -> dict:
    """
    This function creates a dict using a fruit object as reference.
    :param fruit_object: the order object to be converted to dict.
    :return: a dict with fruit data
    """
    fruit_dict = {
        'name': fruit_object.name,
        'price': fruit_object.price / PRICE_DIVISOR,
        'description': fruit_object.description,
        'image': fruit_object.image,
        'vitamins': []
    }

    for vitamin in fruit_object.vitamins:
        fruit_dict['vitamins'].append({
            'name': vitamin.name
        })

    return fruit_dict


@db_session
def liquid_to_dict(liquid_object) -> dict:
    """
    This function creates a dict using a liquid object as reference.
    :param liquid_object: the liquid object to be converted to dict.
    :return: a dict with liquid data
    """
    juice_dict = {
        'name': liquid_object.name,
        'price': liquid_object.price / PRICE_DIVISOR,
        'description': liquid_object.description,
        'image': liquid_object.image,
    }

    return juice_dict
