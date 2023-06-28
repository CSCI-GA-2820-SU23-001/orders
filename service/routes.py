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

# Place your REST API code here ...

######################################################################
#  CREATE AN ORDER
######################################################################

@app.route("/orders", methods=["POST"])
def create_order():
    app.logger.info("Request to Create order...")
    order_data = request.get_json()
    order = Order()
    order.deserialize(order_data)
    order.create()
    app.logger.info("New order %s is created!", order.id)

    res = order.serialize()
    location_url = url_for("read_orders", order_id = order.id, _external = True)
    return jsonify(res), status.HTTP_201_CREATED,{"Location": location_url}

######################################################################
#  UPDATE AN ORDER
######################################################################

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    app.logger.info("Request to list all orders")

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' does not exist.")

    # Update other fields as neededs
    data = request.get_json()
    order.deserialize(data)
    order.update()

    res = order.serialize()
    return jsonify(res), status.HTTP_200_OK

######################################################################
# UPDATE AN ITEM
######################################################################

@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def update_items(order_id, item_id):
    app.logger.info("Request to update Item %s for Order id: %s", item_id, order_id)

    item = Item.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' does not exist.")

    data = request.get_json()
    item.deserialize(data)
    item.update()

    res = item.serialize()
    return jsonify(res), status.HTTP_200_OK


