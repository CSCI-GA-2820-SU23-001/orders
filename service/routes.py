"""
Order Service with Swagger
Paths:
------
GET / - Displays a UI for Selenium testing
GET /orders - Returns a list all of the orders
GET /orders/{order_id} - Returns the orders with a given id number
POST /orders - creates a new order
PUT /orders/{id} - update an order
DELETE /orders/{id} - delete an order
"""
# from flask import Flask
from flask import request, abort
from flask_restx import Resource, fields, reqparse
from service.common import status  # HTTP Status Codes
from service.models import Order, Item, DataValidationError

# Import Flask application
from . import app, api

from sqlalchemy import create_engine

DATABASE_URLS = {
    "dev": "postgresql://postgres:postgres@159.122.183.184:31032/postgres",
    "prod": "postgresql://postgres:postgres@159.122.183.184:31033/postgres"
}
# Assuming you are using 'dev' environment for now.
current_env = "dev"


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")

######################################################################
# GET HEALTH CHECK
######################################################################


@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    # try:
    #     # A simple query to test the database connection and responsiveness.
    #     db.session.execute('SELECT 1')
    # except Exception as e:
    #     # Logging the error is a good practice to diagnose potential DB issues.
    #     app.logger.error(f"Database health check failed: {str(e)}")
    #     return make_response(jsonify(status=503, message="Database Unavailable"), status.HTTP_503_SERVICE_UNAVAILABLE)

    # # If both checks pass, return 200 OK.
    # return make_response(jsonify(status=200, message="OK"), status.HTTP_200_OK)

    try:
        # Creating a new engine for checking health of the database
        engine = create_engine(DATABASE_URLS[current_env])
        connection = engine.connect()
        connection.execute('SELECT 1')
        connection.close()
    except Exception as e:
        # Logging the error is a good practice to diagnose potential DB issues.
        app.logger.error(f"Database health check failed: {str(e)}")
        return make_response(jsonify(status=503, message="Database Unavailable"), status.HTTP_503_SERVICE_UNAVAILABLE)

    # If both checks pass, return 200 OK.
    return {"status": 'OK'}, status.HTTP_200_OK


# Define the model so that the docs reflect what can be sent
create_order_model = api.model(
    "Order",
    {
        "date": fields.Date(required=True, description="The create date of the Order"),
        "total": fields.Float(required=True, description="The total amount of Order"),
        "payment": fields.String(
            required=True,
            enum=["CREDITCARD", "DEBITCARD", "VEMO"],
            description="Payment method (VEMO, CREDITCARD, DEBITCARD) of the Order",
        ),
        # pylint: disable=protected-access
        "address": fields.String(required=True, description="Shipping address of the Order"),
        "customer_id": fields.Integer(required=True, description="The customer who places the Order"),
        "status": fields.String(
            required=True,
            enum=["OPEN", "SHIPPING", "DELIVERED", "CANCELLED"],
            description="Status (OPEN, SHIPPING, DELIVERED, CANCELLED) of the Order",
        ),
    },
)

order_model = api.inherit(
    "OrderModel",
    create_order_model,
    {
        "id": fields.String(
            readOnly=True, description="The order_id assigned internally by service"
        ),
    },
)

create_item_model = api.model(
    "Item",
    {
        "product_id": fields.Integer(required=True, description="The Product ID of the Item"),
        "quantity": fields.Integer(required=True, description="Quantity of this product"),
        "total": fields.Float(required=True, description="The amount of product unit_price * quantity"),
    },
)

item_model = api.inherit(
    "ItemModel",
    create_item_model,
    {
        "id": fields.String(
            readOnly=True, description="The item_id assigned internally by service"
        ),
        "order_id": fields.String(
            readOnly=True, description="Foreign Key order_id"
        ),
    },
)


# query string arguments
order_args = reqparse.RequestParser()
order_args.add_argument(
    "customer_id", type=int, location="args", required=False, help="Query Order by Customer ID"
)
order_args.add_argument(
    "status", type=str, location="args", required=False, help="Query Order by Status"
)



######################################################################
#  PATH: /orders/{order_id}
######################################################################
@api.route("/orders/<order_id>")
@api.param("order_id", "The Order identifier")
class OrderResource(Resource):
    """
    OrderResource class

    Allows the manipulation of a single Order
    GET /order{id} - Returns an Order with the id
    PUT /order{id} - Update an Order with the id
    DELETE /order{id} -  Deletes an Order with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ORDER
    # ------------------------------------------------------------------
    @api.doc("get_orders")
    @api.response(404, "Order not found")
    @api.marshal_with(order_model)
    def get(self, order_id):
        """
        Retrieve a single Order
        This endpoint will return an Order based on its id
        """
        app.logger.info("Request for Order with id: %s", order_id)

        # See if the order exists and abort if it doesn't
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )
        app.logger.info("Returning order: %s", order.id)
        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    #  UPDATE AN ORDER
    # ------------------------------------------------------------------
    @api.doc("update_orders")
    @api.response(404, "Order not found")
    @api.response(400, "The posted Order data was not valid")
    @api.expect(order_model)
    @api.marshal_with(order_model)
    def put(self, order_id):
        """
        Update an Order
        This endpoint will update an Order based the body that is posted
        """
        app.logger.info("Request to update order with id: %s", order_id)

        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' does not exist.")

        # Update other fields as needed
        data = api.payload
        order.deserialize(data)
        order.update()

        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ORDER
    # ------------------------------------------------------------------
    @api.doc("delete_orders")
    @api.response(204, "Order deleted")
    def delete(self, order_id):
        """
        Delete an Order
        This endpoint will delete an order based the id specified in the path
        """
        app.logger.info("Request to delete order with id: %s", order_id)
        account = Order.find(order_id)
        if account:
            account.delete()
            app.logger.info("Order with id [%s] was deleted", order_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders
######################################################################
@api.route("/orders", strict_slashes=False)
class OrderCollection(Resource):
    """
    OrderCollection class

    GET / - List/Query Orders
    POST / - Add a New Order
    """

    # ------------------------------------------------------------------
    # LIST ALL ORDERS
    # ------------------------------------------------------------------
    @api.doc("list_orders")
    @api.expect(order_args, validate=True)
    @api.marshal_list_with(order_model)
    def get(self):
        """Returns all of the Orders"""
        app.logger.info("Request to list all orders")

        orders = []
        args = order_args.parse_args()

        if args["customer_id"] and args["status"]:
            orders = Order.find_by_customer_id_and_status(args["customer_id"], args["status"])
        elif args["customer_id"]:
            orders = Order.find_by_customer_id(args["customer_id"])
        elif args["status"]:
            orders = Order.find_by_status(args["status"])
        else:
            orders = Order.all()

        resp = [order.serialize() for order in orders]
        app.logger.info("[%s] orders returned", len(resp))
        return resp, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW ORDER
    # ------------------------------------------------------------------
    @api.doc("create_orders")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_order_model)
    @api.marshal_with(order_model, code=201)
    def post(self):
        """
        Creates an Order
        This endpoint will create an Order based the data in the body that is posted
        """
        app.logger.info("Request to Create order...")
        order_data = api.payload
        order = Order()
        order.deserialize(order_data)
        order.create()
        app.logger.info("New order %s is created!", order.id)

        resp = order.serialize()
        location_url = api.url_for(OrderResource, order_id=order.id, _external=True)
        return resp, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /orders/{order_id}/cancel
######################################################################
@api.route("/orders/<order_id>/cancel")
@api.param("order_id", "The Order identifier")
class CancelResource(Resource):
    """Cancel action on an Order"""

    @api.doc("cancel_orders")
    @api.response(404, "Order not found")
    @api.response(409, "The Order is not available for cancel")
    def put(self, order_id):
        """Cancel an order changes its status to Cancelled"""
        app.logger.info("Request to cancel an order with id: %s", order_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Order with id '{order_id}' does not exist.")
        if not order.status == "OPEN":
            abort(
                status.HTTP_409_CONFLICT,
                f"Order with id '{order_id}' is already shipped and cannot be cancelled.",
            )
        app.logger.info("Order with iD %s is cancelled", order_id)
        order.status = "CANCELLED"
        order.update()
        return order.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /orders/{order_id}/items
######################################################################
@api.route("/orders/<order_id>/items")
@api.param("order_id", "The Order identifier")
class ItemCollection(Resource):
    """
    ItemCollection class

    GET /order{id}/items - List all Items in an Order
    POST /order{id}/items - Add an Item to an Order
    """

    # ------------------------------------------------------------------
    # LIST ALL ITEMS IN AN ORDER
    # ------------------------------------------------------------------
    @api.doc("list_items")
    @api.expect(order_args, validate=True)
    @api.marshal_list_with(item_model)
    def get(self, order_id):
        """Returns all items for an Order"""
        app.logger.info("Request to list all Items for an order with id: %s", order_id)
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' cannot be found.",
            )
        resp = [item.serialize() for item in order.items]
        return resp, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW ITEM
    # ------------------------------------------------------------------
    @api.doc("add_an_item")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, order_id):
        """Create an Item for an Order"""
        app.logger.info("Request to create an Item for Order with id: %s", order_id)
        # See if the order exists and abort if it doesn't
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' could not be found.",
            )
        elif order.status == "CANCELLED":
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Order with id '{order_id}' has been cancelled.",
            )

        # Create an item from the json data
        item = Item()
        item.deserialize(request.get_json())

        # Append the item to the order
        order.items.append(item)
        order.update()

        # Prepare a message to return
        message = item.serialize()

        return message, status.HTTP_201_CREATED


######################################################################
#  PATH: /orders/{order_id}/items/{item_id}
######################################################################
@api.route("/orders/<order_id>/items/<item_id>")
@api.doc(params={'order_id': "The Order identifier", "item_id": "The Item identifier"})
class ItemResource(Resource):
    """
    ItemResource class

    Allows the manipulation of a single Item
    GET /order{id}/items/item{id} - Returns an Item with the id
    PUT /order{id}/items/item{id} - Update an Item with the id
    DELETE /order{id}/items/item{id} -  Delete an Item with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ITEM FROM AN ORDER
    # ------------------------------------------------------------------
    @api.doc("get_items")
    @api.response(404, "Item not found")
    @api.marshal_with(item_model)
    def get(self, order_id, item_id):
        """Retrieve an Items in an Order"""
        app.logger.info("Request to retrieve an Item with id %s for Order %s", item_id, order_id)
        item = Item.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

        app.logger.info("Returning item: %s", item.id)
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("update_an_item")
    @api.response(404, "Item not found")
    @api.response(400, "The posted Item data was not valid")
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, order_id, item_id):
        """Update an Item"""
        app.logger.info("Request to update Item %s for Order id: %s", item_id, order_id)

        item = Item.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' does not exist.")

        data = request.get_json()
        try:
            item.deserialize(data)
        except DataValidationError:
            abort(status.HTTP_400_BAD_REQUEST, "Invalid quantity detected in item product")

        item.update()
        resp = item.serialize()
        return resp, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_an_item")
    @api.response(204, "Item deleted")
    def delete(self, order_id, item_id):
        """Delete an Order Item"""
        app.logger.info("Request to delete Item %s for Order id: %s", item_id, order_id)
        address = Item.find(item_id)
        if address:
            address.delete()

        return "", status.HTTP_204_NO_CONTENT


# # ------------------------------------------------------------------
# #  CREATE AN ORDER
# # ------------------------------------------------------------------

# @app.route("/orders", methods=["POST"])
# def create_orders():
#     """
#     Creates an Order
#     This endpoint will create an Order based the data in the body that is posted
#     """
#     app.logger.info("Request to Create order...")
#     order_data = request.get_json()
#     order = Order()
#     order.deserialize(order_data)
#     order.create()
#     app.logger.info("New order %s is created!", order.id)

#     resp = order.serialize()
#     location_url = url_for("get_orders", order_id=order.id, _external=True)
#     return jsonify(resp), status.HTTP_201_CREATED, {"Location": location_url}


# # ------------------------------------------------------------------
# #  UPDATE AN ORDER
# # ------------------------------------------------------------------

# @app.route('/orders/<int:order_id>', methods=['PUT'])
# def update_orders(order_id):
#     """
#     Update an Order
#     This endpoint will update an Order based the body that is posted
#     """
#     app.logger.info("Request to list all orders")

#     order = Order.find(order_id)
#     if not order:
#         abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' does not exist.")

#     # Update other fields as neededs
#     data = request.get_json()
#     order.deserialize(data)
#     order.update()

#     resp = order.serialize()
#     return jsonify(resp), status.HTTP_200_OK


# # ------------------------------------------------------------------
# #  CANCEL AN ORDER
# # ------------------------------------------------------------------

# @app.route("/orders/<int:order_id>/cancel", methods=["PUT"])
# def cancel_order(order_id):
#     """Canceling an order changes its status to Cancelled"""
#     app.logger.info("Request to cancel an order with id: %s", order_id)
#     order = Order.find(order_id)
#     if not order:
#         abort(status.HTTP_404_NOT_FOUND,
#               f"Order with id '{order_id}' does not exist.")
#     if not order.status == "OPEN":
#         abort(
#             status.HTTP_409_CONFLICT,
#             f"Order with id '{order_id}' is already shipped and cannot be cancelled.",
#         )
#     app.logger.info("Order with iD %s is cancelled", order_id)
#     order.status = "CANCELLED"
#     order.update()
#     return order.serialize(), status.HTTP_200_OK


# # ------------------------------------------------------------------
# #  LIST ALL ORDERS
# # ------------------------------------------------------------------

# @app.route("/orders", methods=["GET"])
# def list_orders():
#     """Returns all of the Orders"""
#     app.logger.info("Request to list all orders")

#     customer_id_query = request.args.get("customer_id")
#     status_query = request.args.get("status")
#     if customer_id_query and status_query:
#         orders = Order.find_by_customer_id_and_status(customer_id_query, status_query)
#     elif customer_id_query:
#         orders = Order.find_by_customer_id(customer_id_query)
#     elif status_query:
#         orders = Order.find_by_status(status_query)
#     else:
#         orders = Order.all()

#     resp = [order.serialize() for order in orders]
#     app.logger.info("[%s] orders returned", len(resp))
#     return make_response(jsonify(resp), status.HTTP_200_OK)


# # ------------------------------------------------------------------
# #  DELETE AN ORDER
# # ------------------------------------------------------------------

# @app.route("/orders/<int:order_id>", methods=["DELETE"])
# def delete_orders(order_id):
#     """
#     Delete an Order
#     This endpoint will delete an order based the id specified in the path
#     """
#     app.logger.info("Request to delete order with id: %s", order_id)
#     account = Order.find(order_id)
#     if account:
#         account.delete()
#     return make_response("", status.HTTP_204_NO_CONTENT)


# # ------------------------------------------------------------------
# # READ AN ORDER
# # ------------------------------------------------------------------

# @app.route("/orders/<int:order_id>", methods=["GET"])
# def get_orders(order_id):
#     """
#     Retrieve a single Order
#     This endpoint will return an Order based on its id
#     """
#     app.logger.info("Request for Order with id: %s", order_id)

#     # See if the order exists and abort if it doesn't
#     order = Order.find(order_id)
#     if not order:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Order with id '{order_id}' could not be found.",
#         )
#     app.logger.info("Returning order: %s", order.id)
#     return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


# #######################################################################
# #                I T E M S   M E T H O D S
# #######################################################################
# # ------------------------------------------------------------------
# # ADD AN ITEM
# # ------------------------------------------------------------------

# @app.route("/orders/<int:order_id>/items", methods=["POST"])
# def add_items(order_id):
#     """
#     Create an Item on an Order
#     This endpoint will add an item to an order
#     """
#     app.logger.info("Request to create an Item for Order with id: %s", order_id)
#     # See if the order exists and abort if it doesn't
#     order = Order.find(order_id)
#     if not order:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Order with id '{order_id}' could not be found.",
#         )
#     elif order.status == "CANCELLED":
#         abort(
#             status.HTTP_400_BAD_REQUEST,
#             f"Order with id '{order_id}' has been cancelled.",
#         )

#     # Create an item from the json data
#     item = Item()
#     print(request.get_json())
#     item.deserialize(request.get_json())

#     # Append the item to the order
#     order.items.append(item)
#     order.update()

#     # Prepare a message to return
#     message = item.serialize()

#     return make_response(jsonify(message), status.HTTP_201_CREATED)


# # ------------------------------------------------------------------
# # LIST ALL ITEMS
# # ------------------------------------------------------------------

# @app.route("/orders/<int:order_id>/items", methods=["GET"])
# def list_items(order_id):
#     """Returns all of the Items for an Order"""
#     app.logger.info("Request to list all Items for an order with id: %s", order_id)
#     order = Order.find(order_id)
#     if not order:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Order with id '{order_id}' cannot be found.",
#         )
#     resp = [item.serialize() for item in order.items]
#     return make_response(jsonify(resp), status.HTTP_200_OK)


# # ------------------------------------------------------------------
# # RETRIEVE AN ITEM FROM AN ORDER
# # ------------------------------------------------------------------

# @app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
# def get_items(order_id, item_id):
#     """
#     this endpoint returns an item in the order
#     """
#     app.logger.info("Request to retrieve an Item with id %s for Order %s", item_id, order_id)
#     item = Item.find(item_id)
#     if not item:
#         abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

#     app.logger.info("Returning item: %s", item.id)
#     return make_response(jsonify(item.serialize()), status.HTTP_200_OK)


# # ------------------------------------------------------------------
# # UPDATE AN ITEM
# # ------------------------------------------------------------------

# @app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
# def update_items(order_id, item_id):
#     """
#     Update an Item
#     This endpoint will update an Item based the body that is posted
#     """
#     app.logger.info("Request to update Item %s for Order id: %s", item_id, order_id)

#     item = Item.find(item_id)
#     if not item:
#         abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' does not exist.")

#     data = request.get_json()
#     try:
#         item.deserialize(data)
#     except DataValidationError as error:
#         abort(status.HTTP_400_BAD_REQUEST, error)

#     item.update()
#     resp = item.serialize()
#     return jsonify(resp), status.HTTP_200_OK


# # ------------------------------------------------------------------
# # DELETE AN ITEM
# # ------------------------------------------------------------------

# @app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
# def delete_items(order_id, item_id):
#     """
#     Delete an Order Item
#     This endpoint will delete an item based the id specified in the path
#     """
#     app.logger.info("Request to delete Item %s for Order id: %s", item_id, order_id)
#     address = Item.find(item_id)
#     if address:
#         address.delete()

#     return make_response("", status.HTTP_204_NO_CONTENT)


# # ------------------------------------------------------------------
# # Helper function
# # ------------------------------------------------------------------

# def check_content_type(media_type):
#     """Checks that the media type is correct"""
#     content_type = request.headers.get("Content-Type")
#     if content_type and content_type == media_type:
#         return
#     app.logger.error("Invalid Content-Type: %s", content_type)
#     abort(
#         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#         f"Content-Type must be {media_type}",
#     )
