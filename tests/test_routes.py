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
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    ######################################################################
	#  H E L P E R S   F U N C T I O N S   H E R E
	######################################################################

    def _create_order(self, count):
        """ Method to create orders in bulk
		param:
			count -> int: represent the number of orders you want to generate
		"""
        orders = []
		# Need to implement

        return orders
    

    ######################################################################
    #  TESTS FOR LIST ITEMS
    ######################################################################

    def test_list_order_items(self):
        orders = self._create_order(count=10)
        for o in orders:
            o.create()
        item1 = Item(order_id=orders[0].id, id=1)
        item1.create()
        item2 = Item(order_id=orders[0].id, id=2)
        item2.create()
        res = self.client.get(f"/orders/{orders[0].id}/items")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 2)
