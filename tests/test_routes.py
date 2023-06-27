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
from service.models import db, Order, init_db
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
    #  C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    ######################################################################
    #  TESTS FOR READ ORDER
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


    ######################################################################
    #  TESTS FOR READ ITEM
    ######################################################################

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
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], test_order.id)
        self.assertEqual(data["id"], item.id)
