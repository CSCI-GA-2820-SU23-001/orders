"""
My Service

Describe what your service does here
"""
# from flask import Flask
from flask import jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Order, Item, DataValidationError

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        """\n
        create_orders     POST         /orders,\n
        list_orders       GET          /orders,\n
        get_orders        GET          /orders/<order_id>,\n
        update_orders     PUT          /orders/<order_id>,\n
        cancel_order      PUT          /orders/<order_id>/cancel,\n
        delete_orders     DELETE       /orders/<order_id>,\n
        add_items         POST         /orders/<order_id>/items,\n
        list_items        GET          /orders/<order_id>/items,\n
        get_items         GET          /orders/<order_id>/items/<item_id>,\n
        update_items      PUT          /orders/<order_id>/items/<item_id>,\n
        delete_items      DELETE       /orders/<order_id>/items/<item_id>
        """,
        status.HTTP_200_OK,
    )

######################################################################
# GET HEALTH CHECK
######################################################################


@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return make_response(jsonify(status=200, message="OK"), status.HTTP_200_OK)


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
    """
    Creates an Order
    This endpoint will create an Order based the data in the body that is posted
    """
    app.logger.info("Request to Create order...")
    order_data = request.get_json()
    order = Order()
    order.deserialize(order_data)
    order.create()
    app.logger.info("New order %s is created!", order.id)

    resp = order.serialize()
    location_url = url_for("get_orders", order_id=order.id, _external=True)
    return jsonify(resp), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  UPDATE AN ORDER
######################################################################

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_orders(order_id):
    """
    Update an Order
    This endpoint will update an Order based the body that is posted
    """
    app.logger.info("Request to list all orders")

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' does not exist.")

    # Update other fields as neededs
    data = request.get_json()
    order.deserialize(data)
    order.update()

    resp = order.serialize()
    return jsonify(resp), status.HTTP_200_OK


######################################################################
#  CANCEL AN ORDER
######################################################################

@app.route("/orders/<int:order_id>/cancel", methods=["PUT"])
def cancel_order(order_id):
    """Canceling an order changes its status to Cancelled"""
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
#  LIST ALL ORDERS
######################################################################

@app.route("/orders", methods=["GET"])
def list_orders():
    """Returns all of the Orders"""
    app.logger.info("Request to list all orders")

    customer_id_query = request.args.get("customer_id")
    customer_status_query = request.args.get("status")
    if customer_id_query:
        orders = Order.find_by_customer_id(customer_id_query)
    elif customer_status_query:
        orders = Order.find_by_status(customer_status_query)
    else:
        orders = Order.all()

    resp = [order.serialize() for order in orders]
    app.logger.info("[%s] orders returned", len(resp))
    return make_response(jsonify(resp), status.HTTP_200_OK)


######################################################################
#  DELETE AN ORDER
######################################################################

@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
    """
    Delete an Order
    This endpoint will delete an order based the id specified in the path
    """
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
    app.logger.info("Returning order: %s", order.id)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


# ---------------------------------------------------------------------
#                I T E M S   M E T H O D S
# ---------------------------------------------------------------------
######################################################################
# ADD AN ITEM
######################################################################

@app.route("/orders/<int:order_id>/items", methods=["POST"])
def add_items(order_id):
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
    elif order.status == "CANCELLED":
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Order with id '{order_id}' has been cancelled.",
        )

    # Create an item from the json data
    item = Item()
    print(request.get_json())
    item.deserialize(request.get_json())

    # Append the item to the order
    order.items.append(item)
    order.update()

    # Prepare a message to return
    message = item.serialize()

    return make_response(jsonify(message), status.HTTP_201_CREATED)


######################################################################
# LIST ALL ITEMS
######################################################################

@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_items(order_id):
    """Returns all of the Items for an Order"""
    app.logger.info("Request to list all Items for an order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' cannot be found.",
        )
    resp = [item.serialize() for item in order.items]
    return make_response(jsonify(resp), status.HTTP_200_OK)


######################################################################
# RETRIEVE AN ITEM FROM AN ORDER
######################################################################

@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_items(order_id, item_id):
    """
    this endpoint returns an item in the order
    """
    app.logger.info("Request to retrieve an Item with id %s for Order %s", item_id, order_id)
    item = Item.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

    app.logger.info("Returning item: %s", item.id)
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE AN ITEM
######################################################################

@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_items(order_id, item_id):
    """
    Update an Item
    This endpoint will update an Item based the body that is posted
    """
    app.logger.info("Request to update Item %s for Order id: %s", item_id, order_id)

    item = Item.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' does not exist.")

    data = request.get_json()
    try:
        item.deserialize(data)
    except DataValidationError as error:
        abort(status.HTTP_400_BAD_REQUEST, error)

    item.update()
    resp = item.serialize()
    return jsonify(resp), status.HTTP_200_OK


######################################################################
# DELETE AN ITEM
######################################################################

@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(order_id, item_id):
    """
    Delete an Order Item
    This endpoint will delete an item based the id specified in the path
    """
    app.logger.info("Request to delete Item %s for Order id: %s", item_id, order_id)
    address = Item.find(item_id)
    if address:
        address.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# Helper function
######################################################################

def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
