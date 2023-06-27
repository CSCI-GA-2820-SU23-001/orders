"""
Test cases for Order and OrderModel Model

"""
import os
import logging
import unittest
from service.models import Order, DataValidationError, db
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

    def test_read_an_order(self):
        """It should Read an Order"""
        order = OrderFactory()
        order.create()
        found_order = Order.find(order.id)

        self.assertIsNotNone(order)
        self.assertEqual(found_order.id, order.id)
        self.assertEqual(found_order.date, order.date)
        self.assertEqual(found_order.total, order.total)
        self.assertEqual(found_order.payment, order.payment)
        self.assertEqual(found_order.address, order.address)
        self.assertEqual(found_order.customer_id, order.customer_id)
        self.assertEqual(found_order.status, order.status)