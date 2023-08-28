import datetime as dt
import json
from http import HTTPStatus
from unittest import TestCase, mock

from deepdiff import DeepDiff
import pytz
from pony.orm import db_session

import JuiceShop.common as c
from JuiceShop.database import models
from JuiceShop.juice_shop_app import app

DB_FILE_TEST = 'test_db'
DB_CONFIG_TEST = dict(provider='sqlite', filename=DB_FILE_TEST, create_db=True)

test_db = models.define_db(**DB_CONFIG_TEST)

current_clock = dt.datetime(year=2020, month=1, day=1, hour=5, minute=0, second=0, microsecond=5050, tzinfo=pytz.UTC)
uuid_value = '1010101010'


def fake_uuid() -> str:
    return uuid_value


def fake_current_datetime() -> dt.datetime:
    return current_clock


@db_session
def populate_database(db):
    test_vitamins = {
        'VitA': {
            'description': "Description VitA"
        },
        'VitB': {
            'description': "Description VitB"
        }
    }

    test_fruits = {
        'fruit_A': {
            'price': 200,
            'description': "Description fruit_A",
            'image': "some_image_fruit_A",
            'vitamins': ['VitA']
        },
        'fruit_B': {
            'price': 400,
            'description': "Description fruit_B",
            'image': "some_image_fruit_B",
            'vitamins': ['VitA', 'VitB']
        },
    }

    test_liquids = {
        'liquid_A': {
            'price': 200,
            'description': "Description liquid_A",
            'image': "some_image_liquid_A",
        },
        'liquid_B': {
            'price': 400,
            'description': "Description liquid_B",
            'image': "some_image_liquid_B",
        },
    }

    for k, v in test_vitamins.items():
        db.Vitamin(
            name=k,
            description=v['description']
        )

    for k, v in test_fruits.items():
        new_fruit = db.Fruit(
            name=k,
            price=v['price'],
            description=v['description'],
            image=v['image']
        )
        for vit_name in v['vitamins']:
            vitamin = db.Vitamin.get(name=vit_name)
            if vitamin is None:
                continue
            new_fruit.vitamins.add(vitamin)

    for k, v in test_liquids.items():
        db.Liquid(
            name=k,
            price=v['price'],
            description=v['description'],
            image=v['image']
        )


class ApiTestCase(TestCase):

    def setUp(self):
        self.test_db = models.define_db(provider=DB_CONFIG_TEST['provider'],
                                        filename=DB_CONFIG_TEST['filename'],
                                        create_db=True)
        populate_database(self.test_db)

    def tearDown(self):
        self.test_db.drop_all_tables(with_all_data=True)

    @mock.patch('JuiceShop.juice_shop_app.db', test_db)
    def test_get_all_fruits(self):
        test_app = app.test_client()
        response = test_app.get(c.API_VERSION + '/fruits')

        self.assertEqual(response.status_code, HTTPStatus.OK,
                         msg="failed test 'test_get_all_fruits', expected HTTP {}, got {}".format(HTTPStatus.OK,
                                                                                                  response.status_code)
                         )

        response_dict = json.loads(response.data.decode('utf-8'))
        expected = {'fruits': [
            {'description': 'Description fruit_A', 'image': 'some_image_fruit_A', 'name': 'fruit_A', 'price': 2.0,
             'vitamins': [{'description': 'Description VitA', 'name': 'VitA'}]},
            {'description': 'Description fruit_B', 'image': 'some_image_fruit_B', 'name': 'fruit_B', 'price': 4.0,
             'vitamins': [{'description': 'Description VitA', 'name': 'VitA'},
                          {'description': 'Description VitB', 'name': 'VitB'}]}]}

        ddiff = DeepDiff(response_dict, expected, ignore_order=True)
        if len(ddiff) != 0:
            self.fail("test err 'test_get_all_fruits' response. Expected {}, got {}.".format(response_dict, expected))

    @mock.patch('JuiceShop.juice_shop_app.db', test_db)
    def test_get_all_liquids(self):
        test_app = app.test_client()
        response = test_app.get(c.API_VERSION + '/liquids')

        if response.status_code != HTTPStatus.OK:
            self.fail("failed test 'test_get_all_liquids', expected HTTP {}, got {}".format(
                HTTPStatus.OK, response.status_code))

        self.assertEqual(
            response.data, b'{"liquids":[{"description":"Description liquid_A","image":"some_image_liquid'
                           b'_A","name":"liquid_A","price":2.0},{"description":"Description liquid_B","im'
                           b'age":"some_image_liquid_B","name":"liquid_B","price":4.0}]}\n',
            msg="test err 'test_get_all_liquids' response."
        )

    @mock.patch('JuiceShop.juice_shop_app.db', test_db)
    def test_store_new_fruit(self):
        test_app = app.test_client()

        payload = {
            "name": "fruit_C",
            "vitamins": ["VitB"],
            "description": "some description fruit_C",
            "price": 5.0,
            "image": "some_url_path_fruit_C"
        }
        response = test_app.put(c.API_VERSION + '/fruits/store', json=payload)

        if response.status_code != HTTPStatus.OK:
            self.fail("failed test 'test_store_new_fruit', expected HTTP {}, got {}".format(
                HTTPStatus.OK, response.status_code))

        self.assertEqual(
            response.data, b'{"description":"some description fruit_C","image":"some_url_path_fruit_C","n'
                           b'ame":"fruit_C","price":5.0,"vitamins":[{"name":"VitB"}]}\n',
            msg="test err 'test_store_new_fruit' response."
        )

    @mock.patch('JuiceShop.juice_shop_app.db', test_db)
    def test_store_new_liquid(self):
        test_app = app.test_client()

        payload = {
            "name": "liquid_C",
            "description": "some description liquid_C",
            "price": 3.00,
            "image": "some_url_path_liquid_C"
        }
        response = test_app.put(c.API_VERSION + '/liquids/store', json=payload)

        if response.status_code != HTTPStatus.OK:
            self.fail("failed test 'test_store_new_liquid', expected HTTP {}, got {}".format(
                HTTPStatus.OK, response.status_code))

        self.assertEqual(
            response.data, b'{"description":"some description liquid_C","image":"some_url_path_liquid_C",'
                           b'"name":"liquid_C","price":3.0}\n',
            msg="test err 'test_store_new_liquid' response."
        )

    @mock.patch('JuiceShop.juice_shop_app.generate_uuid', fake_uuid)
    @mock.patch('JuiceShop.juice_shop_app.current_datetime', fake_current_datetime)
    @mock.patch('JuiceShop.juice_shop_app.db', test_db)
    def test_order_creation(self):
        test_app = app.test_client()
        endpoint = c.API_VERSION + '/order'
        testcases = [
            {
                'name': 'order with one juice',
                'payload': {
                    "order": [
                        {
                            "fruits": [
                                "fruit_A"
                            ],
                            "liquid": "liquid_A"
                        }
                    ]
                },
                'expected_response': {"is_paid": False, "juices": [
                    {"fruits": [{"name": "fruit_A", "price": 2.0}], "liquid": {"name": "liquid_A", "price": 2.0},
                     "price": 4.0}], "order_at": "Wed, 01 Jan 2020 05:00:00 GMT", "payment_id": "1010101010",
                                      "price": 4.0},
                'expected_http_code': HTTPStatus.OK
            },
            {
                'name': 'order with two juices',
                'payload': {
                    "order": [
                        {
                            "fruits": [
                                "fruit_A",
                                "fruit_B"
                            ],
                            "liquid": "liquid_B"
                        },
                        {
                            "fruits": [
                                "fruit_B"
                            ],
                            "liquid": "liquid_B"
                        },
                    ]
                },
                'expected_response': {'is_paid': False, 'juices': [
                    {'fruits': [{'name': 'fruit_A', 'price': 2.0}, {'name': 'fruit_B', 'price': 4.0}],
                     'liquid': {'name': 'liquid_B', 'price': 4.0}, 'price': 10.0},
                    {'fruits': [{'name': 'fruit_B', 'price': 4.0}], 'liquid': {'name': 'liquid_B', 'price': 4.0},
                     'price': 8.0}], 'order_at': 'Wed, 01 Jan 2020 05:00:00 GMT', 'payment_id': '1010101010',
                                      'price': 18.0},
                'expected_http_code': HTTPStatus.OK
            }
        ]

        for test in testcases:
            response = test_app.post(endpoint, json=test['payload'])
            self.assertEqual(
                response.status_code, test['expected_http_code'],
                msg="test err {}, expected HTTP code {}, got {}".format(test['name'],
                                                                        test['expected_http_code'],
                                                                        response.status_code))
            response_dict = json.loads(response.data.decode('utf-8'))
            ddiff = DeepDiff(response_dict, test['expected_response'], ignore_order=True)
            if len(ddiff) != 0:
                self.fail("test err {}, expected response {}, got {}".format(test['name'],
                                                                             test['expected_response'], response_dict))

    @mock.patch('JuiceShop.juice_shop_app.generate_uuid', fake_uuid)
    @mock.patch('JuiceShop.juice_shop_app.current_datetime', fake_current_datetime)
    @mock.patch('JuiceShop.juice_shop_app.db', test_db)
    def test_update_order(self):
        test_app = app.test_client()
        endpoint = c.API_VERSION + '/order/' + uuid_value

        # create an Order
        order_payload = {
            'order': [
                {
                    'fruits': [
                        'fruit_A'
                    ],
                    'liquid': 'liquid_A'
                }
            ]
        }
        test_app.post(c.API_VERSION + '/order', json=order_payload)

        # update the payment
        order_payment = {
            'is_paid': True
        }
        response = test_app.put(endpoint, json=order_payment)

        if response.status_code != HTTPStatus.OK:
            self.fail("failed test 'test_update_order', expected HTTP {}, got {}".format(
                HTTPStatus.OK, response.status_code))

        self.assertEqual(
            response.data, b'{"is_paid":true,"juices":[{"fruits":[{"name":"fruit_A","price":2.0}],"liquid":{'
                           b'"name":"liquid_A","price":2.0},"price":4.0}],"order_at":"Wed, 01 Jan 2020 05:00:00 GMT",'
                           b'"payment_id":"1010101010","price":4.0}\n',
            msg="test err 'test_update_order' response {}".format(response.data)
        )

    @mock.patch('JuiceShop.juice_shop_app.db', test_db)
    def test_juice_description(self):
        test_app = app.test_client()
        endpoint = c.API_VERSION + '/juice/description'

        juice_payload = {
            'fruits': ["fruit_A", "fruit_B"],
            'liquid': "liquid_B"
        }
        response = test_app.post(endpoint, json=juice_payload)

        if response.status_code != HTTPStatus.OK:
            self.fail("failed test 'test_juice_description', expected HTTP {}, got {}".format(
                HTTPStatus.OK, response.status_code))

        response_dict = json.loads(response.data.decode('utf-8'))
        expected = {
            'fruits': [{'description': 'Description fruit_A', 'name': 'fruit_A'},
                       {'description': 'Description fruit_B', 'name': 'fruit_B'}],
            'liquid': {'description': 'Description liquid_B', 'name': 'liquid_B'},
            'vitamins': [{'description': 'Description VitA', 'name': 'VitA'},
                         {'description': 'Description VitA', 'name': 'VitA'},
                         {'description': 'Description VitB', 'name': 'VitB'}]}

        ddiff = DeepDiff(response_dict, expected, ignore_order=True)
        if len(ddiff) != 0:
            self.fail("test err 'test_juice_description' response {}".format(expected, response_dict))
