"""
Test cases for Order and OrderModel Model

"""
import os
import logging
import unittest
from service.models import Order, Item, DataValidationError, db
from tests.factories import OrderFactory, ItemFactory


######################################################################
#  YourResourceModel   M O D E L   T E S T   C A S E S
######################################################################
class TestOrder(unittest.TestCase):
    """ Test Cases for Order Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """

    def tearDown(self):
        """ This runs after each test """

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_example_replace_this(self):
        """ It should always be true """
        self.assertTrue(True)


    def test_create_an_order(self):
        """ It should Create an Order and assert that it exists """
        fake_order = OrderFactory()
        # pylint: disable=unexpected-keyword-arg
        order = Order(
            date=fake_order.date,
            total=fake_order.total,
            payment=fake_order.payment,
            address=fake_order.address,
            customer_id=fake_order.customer_id,
            status=fake_order.status
        )
        self.assertIsNotNone(order)
        self.assertEqual(order.id, None)
        self.assertEqual(order.date, fake_order.date)
        self.assertEqual(order.total, fake_order.total)
        self.assertEqual(order.payment, fake_order.payment)
        self.assertEqual(order.address, fake_order.address)
        self.assertEqual(order.customer_id, fake_order.customer_id)
        self.assertEqual(order.status, fake_order.status)

    def test_add_an_order(self):
        """ It should Create an order and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
