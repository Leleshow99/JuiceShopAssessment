from pony.orm import db_session, select


@db_session
def get_all_fruits(db: db_session) -> list:
    """

    :param db: DB Connection
    :return: Expense Object
    """
    return list(
        select(
            f for f in db.Fruit
        ))


@db_session
def get_all_liquids(db: db_session) -> list:
    """

    :param db: DB Connection
    :return: Expense Object
    """
    return list(
        select(
            l for l in db.Liquid
        ))


@db_session
def get_all_juices(db: db_session) -> list:
    """

    :param db:
    :return:
    """
    return list(
        select(
            j for j in db.Juice
        )
    )


@db_session
def get_fruit_by_name(db: db_session, fruit_name: str):
    """

    :param db:
    :param fruit_name:
    :return:
    """
    return db.Fruit.get(name=fruit_name)


@db_session
def get_liquid_by_name(db: db_session, liquid_name: str):
    """

    :param db:
    :param liquid_name:
    :return:
    """
    return db.Liquid.get(name=liquid_name)


@db_session
def get_vitamin_by_name(db: db_session, vitamin_name: str):
    """

    :param db:
    :param vitamin_name:
    :return:
    """
    return db.Vitamin.get(name=vitamin_name)


@db_session
def get_order_by_payment_id(db: db_session, payment_id: str):
    """

    :param payment_id:
    :param db:
    :return:
    """
    return db.Order.get(payment_id=payment_id)
