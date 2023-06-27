
    app.logger.info("Returning item: %s", item.name)
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)
    res = order.serialize()
    location_url = url_for("read_orders", order_id = order.id, _external = True)
    return jsonify(res), status.HTTP_201_CREATED,{"Location": location_url}