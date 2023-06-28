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
from service.models import db, Order, Item
from tests.factories import ItemFactory, OrderFactory
from service.common import status  # HTTP Status Codes


######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """
        self.client = app.test_client()

    def tearDown(self):
        """ This runs after each test """
    
    ######################################################################
    #  H E L P E R S   F U N C T I O N S   H E R E
    ######################################################################

    def _create_orders(self, count):
        """ Method to create orders in bulk
            count -> int: represent the number of orders you want to generate
		"""
        orders = []
        # Need to implement

        return orders
    
    def _create_items(self, count):
        """ Method to create items in bulk
            count -> int: represent the number of items you want to generate
		"""
        items = []
        # Need to implement

        return items
    
    ######################################################################
    # #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    ######################################################################
    #  O R D E R S  T E S T  C A S E
    ######################################################################

    def test_list_orders(self):
        """ It should list all orders """
        self._create_orders(4)
        resp = self.client.get("/orders")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 4)


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

    ######################################################################
    #  I T E M S  T E S T  C A S E
    ######################################################################

    def test_list_items(self):
        """ It should list all items for an order """
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