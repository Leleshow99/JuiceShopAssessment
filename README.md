# Juice Shop


## Table of Contents

1. [Introduction](#Introduction)
2. [How to Run](#how-to-run)
3. [APIs Description](#apis-descriptions)
4. [Testing APIs](#testing-apis)

## Introduction
This code implements the backend APIs to be used in a Juice Shop. The Juice Shop could use this code to build
an online version of its Menu, where customers can create the Juices and order.

The frontend could be easily attached to the APIs exposed in this code, so the Juice Shop has the freedom to choose
the best technology on each case.

## How to Run
This section shows how to install the server and run. We provided a python script that can be used to initialise and
run the server with a small number of ingredients. 

### Installing Dependencies and Running
Follow the steps below to prepare and install dependencies to run the server. The steps bellow assumes you are using 
python 3.10 or later. 

* Inside the root directory, creates the virtual environment and activate it: 
```bash
python3 -m venv myenv
source myenv/bin/activate
```

* Now, install the requirements packages to run.
```bash
pip install -r requirements.txt
```

* Now you are ready to run the server. 
```bash
./myenv/bin/python run_juice_shop_app.py
```

If you want to initialize the database, run the script using the `-c` parameter.
```bash
./myenv/bin/python run_juice_shop_app.py -c
```

### Running Unit Tests
To run the unit tests. 

```bash
./myenv/bin/python -m unittest JuiceShop.tests.view_tests.ApiTestCase -v
```

## APIs Descriptions
The server has several endpoints that can be used to easily plug a frontend. Find below the endpoints descriptions with
the expected HTTP method and response.

Current API version is `v1`. All endpoints have the version as prefix.

---

* `/fruits`

**HTTP Methods:** `GET`

**DESCRIPTION:** List all fruits available. It can be used to show customers the available fruit options.

---

* `/liquids`

**HTTP Methods:** `GET`

**DESCRIPTION:** List all liquids available. It can be used to show customers the available liquids options.

---

* `/fruits/store`

**HTTP Methods:** `PUT`

**DESCRIPTION:** Used to create or update new fruits. This endpoint is for shop internal usage. If the fruit name
already exists, it will be updated.

**PAYLOAD:** This endpoint expects a json as payload. 

```json
{
  "name": "new_fruit",
  "vitamins": ["C", "B16"],
  "description": "some description",
  "price": 4.5,
  "image": "some_url_or_path"
}
```

---

* `/liquids/store`

**HTTP Methods:** `PUT`

**DESCRIPTION:** Used to create or update new liquids. This endpoint is for shop internal usage. If the liquid name
already exists, it will be updated.

**PAYLOAD:** This endpoint expects a json as payload. 

```json
{
  "name": "new_liquid",
  "description": "some description",
  "price": 5.00,
  "image": "some_url_or_path"  
}
```

---

* `/juices`

**HTTP Methods:** `GET`

**DESCRIPTION:** List all juices ordered. This endpoint is also an internal endpoint that can be used to check most
popular juices, prices, etc.

---

* `/order`

**HTTP Methods:** `POST`

**DESCRIPTION:** Creates an order to be paid. This endpoint receives a list of juices and returns an order details, 
such as total price and an ID to customer pay.

**PAYLOAD:** This endpoint expects a json as payload.

```json
{
  "order": [
    {
      "fruits": [
        "banana",
        "orange"
      ],
      "liquid": "milk"
    },
    {
      "fruits": [
        "banana",
        "mango"
      ],
      "liquid": "water"
    },
    {
      "fruits": [
        "banana",
        "mango",
        "orange"
      ],
      "liquid": "milk"
    }
  ]
}
```

---

* `/order/<string:payment_id>`

**HTTP METHODS:** `GET`, `PUT`

**DESCRIPTION:** This endpoint is used to retrieve the payment status of an order (`GET`) or to update the order payment
status (`PUT`). 

**PAYLOAD:** To update an order, this endpoint should receive the following payload.

```json
{
  "is_paid": true
}
```

---

* `/juice/description`

**HTTP METHODS:** `POST`

**DESCRIPTION:** This endpoint returns a description of a given juice. It receives a payload with the juice's ingredients
and return a json with the description about the juice's benefits and vitamins for each ingredient.

**PAYLOAD:** To get the juice's description, this endpoint receives a juice as payload.

```json
    {
      "fruits": [
        "banana",
        "orange"
      ],
      "liquid": "milk"
    }
```

## Testing APIs
You can test the server API using the command `curl` for endpoints that accepts `PUT` or `POST` HTTP methods. For 
endpoints that accepts `GET` you can use your browser. 

Assuming you are running the server in your localhost and using port 8000. To test the API with a `POST`, just run:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"order": [{"fruits": ["banana","orange"],"liquid": "milk"},{"fruits": ["banana","mango"],"liquid": "water"},{"fruits": ["banana","mango","orange"],"liquid": "milk"}]}' http://127.0.0.1:8000/v1/order
```
