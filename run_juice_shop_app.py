import sys

from pony.orm import db_session, select

import JuiceShop.common as c
from JuiceShop.database import models
from JuiceShop.juice_shop_app import app

HTTP_PORT = 8000
HOST = '127.0.0.1'

db = models.define_db(
    provider='sqlite',
    filename=c.DB_FILE,
    create_db=True
)

VITAMINS = {
    'C': {
        'description': "Vitamin C (ascorbic acid) is a nutrient your body needs to form blood vessels, cartilage, "
                       "muscle and collagen in bones. Vitamin C is also vital to your body's healing process."
    },
    'D': {
        'description': "A fat-soluble vitamin that is naturally present in a few foods, added to others, "
                       "and available as a dietary supplement. It is also produced endogenously when ultraviolet "
                       "(UV) rays from sunlight strike the skin and trigger vitamin D synthesis."
    },
    'B6': {
        'description': "Vitamin B6, or pyridoxine, is a water-soluble vitamin found naturally in many foods, "
                       "as well as added to foods and supplements. Pyridoxal 5' phosphate (PLP) is the active "
                       "coenzyme form and most common measure of B6 blood levels in the body."

    },
}

FRUITS = {
    'banana': {
        'price': 450,
        'description': "A banana is a popular tropical fruit known for its sweet taste and high nutritional content.",
        'vitamins': ['C', 'B6'],
        'image': "http://someurl.com/image/banana.jpeg"
    },
    'orange': {
        'price': 400,
        'description': "An orange is a citrus fruit appreciated for its juicy, tangy flavor and its rich source of "
                       "vitamin C.",
        'vitamins': ['C'],
        'image': "http://someurl.com/image/orange.jpeg"
    },
    'mango': {
        'price': 600,
        'description': "A mango is a tropical fruit cherished for its succulent flesh and distinctively sweet and "
                       "aromatic taste",
        'vitamins': ['C', 'D'],
        'image': "http://someurl.com/image/mango.jpeg"
    }
}

LIQUIDS = {
    'water': {
        'price': 200,
        'description': "Water supports vital bodily functions, aids digestion, and helps maintain overall hydration "
                       "and wellness.",
        'image': "http://someurl.com/image/water.jpeg"
    },
    'milk': {
        'price': 300,
        'description': "Milk provides essential nutrients like calcium and protein, contributing to strong bones and "
                       "overall health.",
        'image': "http://someurl.com/image/milk.jpeg"
    }
}


@db_session
def add_vitamins():
    """
    Initial load to the database. It adds a set of Vitamins.
    :return: None
    """

    for k, v in VITAMINS.items():
        try:
            db.Vitamin(
                name=k,
                description=v['description']
            )
        except Exception as e:
            raise Exception("Unable to Create Vitamin - {}".format(e))


@db_session
def add_fruits():
    """
    Initial load to the database. It adds a set of Fruits and associate them to the Vitamins.
    :return: None
    """
    for k, v in FRUITS.items():
        try:
            new_fruit = db.Fruit(
                name=k,
                price=v['price'],
                description=v['description'],
                image=v['image'])
            for vit_name in v['vitamins']:
                vit = select(
                    v for v in db.Vitamin if v.name == vit_name)
                new_fruit.vitamins.add(vit)
        except Exception as e:
            raise Exception("Unable to Create Fruit - {}".format(e))


@db_session
def add_liquids():
    """
    Initial load to the database. It adds a set of Liquids to be used when making a juice.
    :return: None
    """
    for k, v in LIQUIDS.items():
        try:
            db.Liquid(
                name=k,
                price=v['price'],
                description=v['description'],
                image=v['image'])
        except Exception as e:
            raise Exception("Unable to Create Liquid - {}".format(e))


if __name__ == '__main__':
    args_len = len(sys.argv)
    if args_len >= 2 and sys.argv[1] == '-c':
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        print("Creating and populating DB...\n")
        print("Creating the Vitamins")
        add_vitamins()

        print("Creating the Fruits")
        add_fruits()

        print("Creating the Liquids")
        add_liquids()

    app.run(host=HOST, port=HTTP_PORT)
