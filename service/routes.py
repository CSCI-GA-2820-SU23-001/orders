"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import YourResourceModel

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

######################################################################
# READ AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods = ["GET"])
def get_orders(order_id):
    """
    Retrieve a single order
    """
    app.logger.info("Request for Order with id: %s", order_id)

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    app.logger.info("Returning order: %s", order.name)
    return jsonify(order.serialize()), status.HTTP_200_OK

# ---------------------------------------------------------------------
#                ITEMS   M E T H O D S
# ---------------------------------------------------------------------

######################################################################
# RETRIEVE AN ITEM FROM AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods = ["GET"])
def get_items(order_id, item_id):
    """
    this endpoint returns an item in the order
    """
    app.logger.info("Request to retrieve an Item with id %s for Order %s", item_id, order_id)
    item = Item.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

    app.logger.info("Returning item: %s", item.name)
    return jsonify(item.serialize()), status.HTTP_200_OK