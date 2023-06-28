"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import db, Order, Item, init_db
from tests.factories import ItemFactory, OrderFactory
from service.common import status  # HTTP Status Codes
from datetime import date
from itertools import cycle


######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once after test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()
    
    ######################################################################
    #  H E L P E R S   F U N C T I O N S   H E R E
    ######################################################################

    def _create_orders(self, count):
        """ Method to create orders in bulk
            count -> int: represent the number of orders you want to generate
		"""
        orders = []
        # Need to implement
        # Define the constant status values
        status_values = ["OPEN","SHIPPING","DELIVERED","CANCELLED"]
        # Create a cycle iterator for status values
        status_cycle = cycle(status_values)

        for _ in range(count):
            # Get the next status value from the cycle
            status_value = next(status_cycle)
            # Pass the status value to the factory
            order = OrderFactory(status=status_value)
            resp = self.client.post("/orders", json=order.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Order",
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)

        return orders
    
    ######################################################################
    # #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


    # ---------------------------------------------------------------------
    #               O R D E R  M E T H O D S
    # ---------------------------------------------------------------------

    ######################################################################
    #  TEST CREATE / ADD ORDER
    ######################################################################
    def test_create_orders(self):
        """ It should create an order """
        order = OrderFactory()
        res = self.client.post(
            "/orders",
            json = order.serialize(), 
            content_type = "application/json"
        )
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        self.assertIsNotNone(orders[0].id)

        location = res.headers.get("location", None)
        self.assertIsNotNone(location)

        data = res.get_json()
        # self.assertEqual(data["date"], order.date,"date does not match")
        self.assertEqual(data["total"],order.total, "total price does not match")
        self.assertEqual(data["payment"],order.payment, "payment does not match")
        self.assertEqual(data["address"],order.address, "address does not match")
        self.assertEqual(data["customer_id"],order.customer_id, "customer_id does not match")
        self.assertEqual(data["status"],order.status, "status does not match")

    def test_create_order_missing_info(self):
        """
        It should fail if the call has some missing information.
        """
        res = self.client.post(
            "/orders",
            json={
                "products": []
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        orders = Order.all()
        self.assertEqual(len(orders), 0)
    
    ######################################################################
    #  TEST DELETE ORDER
    ######################################################################
    def test_delete_orders(self):
        """It should Delete an Order"""
        order = self._create_orders(1)[0]
        res = self.client.post(
            f"/orders",
            json=order.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        data = res.get_json()
        logging.debug(data)
        order_id = data["id"]

        resp = self.client.delete(f"orders/{order_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
    

    # ---------------------------------------------------------------------
    #               I T E M  M E T H O D S
    # ---------------------------------------------------------------------
    ######################################################################
    #  TEST ADD ITEM IN ORDER
    ######################################################################

    def test_add_item(self):
        """It should Add an item to an order"""
        order = self._create_orders(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.get_json()
        logging.debug(data)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["total"], item.total)
        self.assertEqual(data["order_id"], order.id)

    ######################################################################
    #  TEST LIST ITEMS
    ######################################################################

    def test_list_items(self):
        order = self._create_orders(1)[0]
        item = ItemFactory()
        res = self.client.post(
            f"/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        data = res.get_json()
        logging.debug(data)
        item_id = data["id"]

        res = self.client.get(
            f"/orders/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["quantity"], item.quantity)
    
    ######################################################################
    #  TEST DELETE ITEMS
    ######################################################################

    def test_delete_items(self):
        """It should Delete an Item"""
        # get the id of an account
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.client.post(
            f"orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"orders/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure address is not there
        resp = self.client.get(
            f"orders/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)