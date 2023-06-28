"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Order, Item

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# ---------------------------------------------------------------------
#               O R D E R  M E T H O D S
# ---------------------------------------------------------------------

######################################################################
#  CREATE AN ORDER
######################################################################

@app.route("/orders", methods=["POST"])
def create_orders():
    app.logger.info("Request to Create order...")
    order_data = request.get_json()
    order = Order()
    order.deserialize(order_data)
    order.create()
    app.logger.info("New order %s is created!", order.id)

    res = order.serialize()
    location_url = url_for("get_orders", order_id = order.id, _external = True)
    return jsonify(res), status.HTTP_201_CREATED,{"Location": location_url}

######################################################################
#  DELETE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
    app.logger.info("Request to delete order with id: %s", order_id)
    account = Order.find(order_id)
    if account:
        account.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# READ AN ORDER
######################################################################


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_orders(order_id):
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
    app.logger.info("Returning order: %s", order.name)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)

# ---------------------------------------------------------------------
#                I T E M S   M E T H O D S
# ---------------------------------------------------------------------
######################################################################
# ADD AN ITEM
######################################################################

@app.route("/orders/<int:order_id>/items", methods=["POST"])
def create_items(order_id):
    """
    Create an Item on an Order
    This endpoint will add an item to an order
    """
    app.logger.info("Request to create an Item for Order with id: %s", order_id)
    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # Create an item from the json data
    item = Item()
    item.deserialize(request.get_json())

    # Append the item to the order
    order.products.append(item)
    order.update()

    # Prepare a message to return
    message = item.serialize()

    return make_response(jsonify(message), status.HTTP_201_CREATED)

######################################################################
# LIST AN ITEM
######################################################################

@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_items(order_id):
    app.logger.info("Request to list all Items for an order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' cannot be found.",
        )
    res = [item.serialize() for item in order.items]
    return make_response(jsonify(res), status.HTTP_200_OK)

######################################################################
# DELETE AN ITEM
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(order_id, item_id):
    app.logger.info("Request to delete Item %s for Order id: %s", item_id, order_id)
    address = Item.find(item_id)
    if address:
        address.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)