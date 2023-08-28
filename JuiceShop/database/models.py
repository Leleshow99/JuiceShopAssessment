from datetime import datetime

from pony.orm import Database, Optional, PrimaryKey, Set


def define_entities(db):
    class Fruit(db.Entity):
        id = PrimaryKey(int, auto=True)
        name = Optional(str)
        price = Optional(int)
        description = Optional(str)
        image = Optional(str)
        vitamins = Set('Vitamin')
        juices = Set('Juice')

    class Liquid(db.Entity):
        id = PrimaryKey(int, auto=True)
        name = Optional(str)
        price = Optional(int)
        description = Optional(str)
        image = Optional(str)
        juices = Set('Juice')

    class Vitamin(db.Entity):
        id = PrimaryKey(int, auto=True)
        name = Optional(str)
        description = Optional(str)
        fruits = Set(Fruit)

    class Juice(db.Entity):
        id = PrimaryKey(int, auto=True)
        price = Optional(int)
        fruits = Set(Fruit)
        liquid = Optional(Liquid)
        order = Optional('Order')

    class Order(db.Entity):
        id = PrimaryKey(int, auto=True)
        juices = Set(Juice)
        price = Optional(int)
        payment_id = Optional(str)
        order_at = Optional(datetime, volatile=True)
        is_paid = Optional(bool, volatile=True)


def define_db(**db_params):
    db = Database(**db_params)
    define_entities(db)
    db.generate_mapping(create_tables=True)

    return db
