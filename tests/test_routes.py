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
from tests.factories import OrderFactory, ItemFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/orders"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestOrderServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    def setUp(self):
        """ This runs before each test """
        self.client = app.test_client()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
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
    
    def test_get_order(self):
        """It should Read a single Order"""
        # get the id of an order
        test_order = self._create_orders(1)[0]
        response = self.client.get(
            f"{BASE_URL}/{test_order.id}", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], test_order.id)

    def test_get_order_not_found(self):
        """It should not Read an Order that is not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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


    def test_get_item(self):
        """It should Read an item from an order"""

        test_order = self._create_orders(1)[0]
        item = ItemFactory()
        response = self.client.post(
            f"{BASE_URL}/{test_order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.get_json()
        logging.debug(data)
        item_id = data["id"]

        response = self.client.get(
            f"{BASE_URL}/{test_order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], test_order.id)
        self.assertEqual(data["id"], item.id)

    
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