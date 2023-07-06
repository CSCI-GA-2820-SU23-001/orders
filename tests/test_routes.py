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


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/orders"
NONEXIST_ORDER_ID = "1234"
NONEXIST_ITEM_ID = "1234"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestOrderServer(TestCase):
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
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

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
            resp = self.client.post(f"{BASE_URL}", json=order.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Order",
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)

        return orders

    # ---------------------------------------------------------------------
    #               O R D E R  M E T H O D S
    # ---------------------------------------------------------------------

    ######################################################################
    #  TEST CREATE / ADD ORDER
    ######################################################################
    def test_create_orders(self):
        """ It should create an order """
        order = OrderFactory(status="OPEN")  # Create an order with 'in progress' status
        res = self.client.post(
            f"{BASE_URL}",
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
            f"{BASE_URL}",
            json={
                "items": []
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        orders = Order.all()
        self.assertEqual(len(orders), 0)

    ######################################################################
    #  TEST LIST ORDER
    ######################################################################

    def test_list_orders(self):
        """ It should list all orders """
        self._create_orders(4)
        resp = self.client.get(f"{BASE_URL}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 4)

    ######################################################################
    #  TEST GET ORDER
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
    #  TEST UPDATE ORDER
    ######################################################################

    def test_update_orders(self):
        """It should update an Order"""
        order = self._create_orders(1)[0]
        res = self.client.post(
            f"{BASE_URL}",
            json=order.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        data = res.get_json()
        logging.debug(data)
        order_id = data["id"]

        # Modify the order with the desired changes
        new_total = 100.00
        order.total = new_total
        res = self.client.put(
            f"{BASE_URL}/{order_id}",
            json=order.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
            
        # Get the updated order from the response
        updated_order = res.get_json()
        # Assert that the total of the updated order matches the new total
        self.assertEqual(updated_order["total"], new_total)

    def test_update_nonexist_orders(self):
        """It Should update an non-existing order"""
        resp = self.client.put(f"{BASE_URL}/{NONEXIST_ORDER_ID}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  TEST DELETE ORDER
    ######################################################################

    def test_delete_orders(self):
        """It should Delete an Order"""
        order = self._create_orders(1)[0]
        res = self.client.post(
            f"{BASE_URL}",
            json=order.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        data = res.get_json()
        logging.debug(data)
        order_id = data["id"]

        resp = self.client.delete(f"{BASE_URL}/{order_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_nonexist_orders(self):
        """It Should Delete an non-existing order"""
        resp = self.client.delete(f"{BASE_URL}/{NONEXIST_ORDER_ID}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    ######################################################################
    #  TEST CANCEL ORDER
    ######################################################################

    def test_cancel_order(self):
        """It should cancel an order"""
        orders = self._create_orders(3)
        open_orders = [order for order in orders if order.status == "OPEN"]
        order = open_orders[0]
        resp = self.client.put(f"{BASE_URL}/{order.id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.get(f"{BASE_URL}/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["status"], "CANCELLED")

    def test_cancel_nonexist_order(self):
        """It should cancel an non-existing order"""
        resp= self.client.put(f"{BASE_URL}/{NONEXIST_ORDER_ID}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_cancel_order_not_open(self):
        """It should not cancel an order that isn't in open status"""
        orders = self._create_orders(10)
        open_orders = [order for order in orders if order.status == "SHIPPING"]
        order = open_orders[0]
        resp = self.client.put(f"{BASE_URL}/{order.id}/cancel")
        self.assertEqual(resp.status_code, 409)

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
            f"{BASE_URL}/{order.id}/items",
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

    def test_add_item_nonexist_order(self):
        """It should Add an item to an non-existing order"""
        resp= self.client.post(f"{BASE_URL}/{NONEXIST_ORDER_ID}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  TEST LIST ITEMS
    ######################################################################

    def test_list_items(self):
        """ It should list all items for an order """
        test_order = self._create_orders(1)[0]
        response = self.client.get(
            f"{BASE_URL}/{test_order.id}/items"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_items_nonexist_order(self):
        """It should list all items for an non-existing order"""
        resp= self.client.get(f"{BASE_URL}/{NONEXIST_ORDER_ID}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  TEST GET ITEMS
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
        self.assertEqual(data["order_id"], test_order.id)
        # self.assertEqual(data["id"], item.id) #BUG

    ######################################################################
    #  TEST UPDATE ITEMS
    ######################################################################

    def test_update_items(self):
        """It should update an item within an order"""
        # Create an order
        order = self._create_orders(1)[0]

        # Create an item
        item = ItemFactory(order_id=order.id)

        # Add the item to the order
        res = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.get_json()
        item_id = data["id"]

        # Modify the item with the desired changes
        new_quantity = 2
        item.quantity = new_quantity

        # Update the item within the order
        res = self.client.put(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Get the updated item from the response
        updated_item = res.get_json()

        # Assert that the quantity of the updated item matches the new quantity
        self.assertEqual(updated_item["quantity"], new_quantity)

    def test_update_nonexist_items(self):
        """It should update a non-existing item"""
        order = self._create_orders(1)[0]

        # retrieve it back and make sure item is not there
        res = self.client.get(
            f"{BASE_URL}/{order.id}/items/{NONEXIST_ITEM_ID}",
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

         # send update request
        res = self.client.put(
            f"{BASE_URL}/{order.id}/items/{NONEXIST_ITEM_ID}",
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  TEST DELETE ITEMS
    ######################################################################

    def test_delete_items(self):
        """It should Delete an Item"""
        # get the id of an account
        order = self._create_orders(1)[0]
        
        item = ItemFactory(order_id=order.id)
        res = self.client.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = res.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        res = self.client.delete(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure address is not there
        res = self.client.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_nonexist_items(self):
        """It should Delete a non-existing item"""
        order = self._create_orders(1)[0]

        # retrieve it back and make sure item is not there
        res = self.client.get(
            f"{BASE_URL}/{order.id}/items/{NONEXIST_ITEM_ID}",
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

         # send delete request
        res = self.client.delete(
            f"{BASE_URL}/{order.id}/items/{NONEXIST_ITEM_ID}",
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    ######################################################################
    #  TEST BAD REQUEST
    ######################################################################

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        order = OrderFactory()
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_index(self):
        """It should call the Home Page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


