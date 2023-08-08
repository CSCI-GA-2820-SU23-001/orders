"""
Test cases for Order and OrderModel Model

"""
# import os
import logging
import unittest
from service import app
from service.models import Order, Item, DataValidationError, db
from tests.factories import OrderFactory, ItemFactory


######################################################################
#  O R D E R   M O D E L   T E S T   C A S E S
######################################################################
class TestOrder(unittest.TestCase):
    """ Test Cases for Order Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Order.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """
        db.session.query(Order).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_example_replace_this(self):
        """ It should always be true """
        self.assertTrue(True)

    # ---------------------------------------------------------------------
    #               O R D E R  M E T H O D S
    # ---------------------------------------------------------------------

    ######################################################################
    #  TEST CREATE / ADD ORDER
    ######################################################################
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

    def test_list_all_orders(self):
        """It should list all orders in the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        for order in OrderFactory.create_batch(3):
            order.create()
        orders = Order.all()
        self.assertEqual(len(orders), 3)

    def test_update_an_order(self):
        """ It should update an Order """
        orders = Order.all()
        self.assertEqual(orders, [])

        order = OrderFactory()
        order.create()
        self.assertIsNotNone(order.id)

        fake_order = OrderFactory()
        order.date = fake_order.date
        order.total = fake_order.total
        order.payment = fake_order.payment
        order.address = fake_order.address
        order.customer_id = fake_order.customer_id
        order.status = fake_order.status
        order.update()

        updated_order = Order.find(order.id)

        self.assertEqual(updated_order.id, order.id)
        self.assertEqual(updated_order.date, fake_order.date)
        self.assertEqual(updated_order.total, fake_order.total)
        self.assertEqual(updated_order.payment, fake_order.payment)
        self.assertEqual(updated_order.address, fake_order.address)
        self.assertEqual(updated_order.customer_id, fake_order.customer_id)
        self.assertEqual(updated_order.status, fake_order.status)

    def test_delete_an_order(self):
        """It should Delete an order from the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        order.create()
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        order = orders[0]
        order.delete()
        orders = Order.all()
        self.assertEqual(len(orders), 0)

    def test_cancel_order(self):
        """It should change the status of an order to CANCELLED"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        order.create()
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        order = orders[0]
        order.status = "CANCELLED"
        order.update()
        orders = Order.all()
        self.assertEqual(order.status, "CANCELLED")

    def test_find_by_status(self):
        """It should find an order by status"""
        order = OrderFactory()
        order.create()
        same_order = Order.find_by_status(order.status)[0]
        self.assertEqual(same_order.id, order.id)
        self.assertEqual(same_order.status, order.status)

    def test_find_by_customer_id(self):
        """It should find an order by customer id"""
        order = OrderFactory()
        order.create()
        same_order = Order.find_by_customer_id(order.customer_id)[0]
        self.assertEqual(same_order.id, order.id)
        self.assertEqual(same_order.customer_id, order.customer_id)

    def test_find_by_customer_id_and_status(self):
        """It should find an order by customer id and status"""
        order = OrderFactory()
        order.create()
        same_order = Order.find_by_customer_id_and_status(order.customer_id, order.status)[0]
        self.assertEqual(same_order.id, order.id)
        self.assertEqual(same_order.customer_id, order.customer_id)
        self.assertEqual(same_order.status, order.status)

    ######################################################################
    #  TEST SERIALIZE / DESERIALIZE ORDER
    ######################################################################
    def test_serialize_an_order(self):
        """It should Serialize an order"""
        order = OrderFactory()
        item = ItemFactory()
        order.items.append(item)
        serial_order = order.serialize()
        self.assertEqual(serial_order["id"], order.id)
        self.assertEqual(serial_order["date"], str(order.date))
        self.assertEqual(serial_order["total"], order.total)
        self.assertEqual(serial_order["payment"], str(order.payment))
        self.assertEqual(serial_order["address"], order.address)
        self.assertEqual(serial_order["customer_id"], order.customer_id)
        self.assertEqual(serial_order["status"], str(order.status))
        self.assertEqual(len(serial_order["items"]), 1)
        items = serial_order["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["product_id"], item.product_id)
        self.assertEqual(items[0]["quantity"], item.quantity)
        self.assertEqual(items[0]["total"], item.total)
        self.assertEqual(items[0]["order_id"], item.order_id)

    def test_deserialize_an_order(self):
        """It should Deserialize an order"""
        order = OrderFactory()
        order.items.append(ItemFactory())
        order.create()
        serial_order = order.serialize()
        new_order = Order()
        new_order.deserialize(serial_order)
        self.assertEqual(new_order.total, order.total)
        # self.assertEqual(new_order.date, order.date)
        self.assertEqual(new_order.payment, order.payment)
        self.assertEqual(new_order.address, order.address)
        self.assertEqual(new_order.customer_id, order.customer_id)
        self.assertEqual(new_order.status, order.status)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an order with a KeyError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an order with a TypeError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, [])

    def test_deserialize_with_value_error(self):
        """It should not Deserialize an order with a ValueError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, [])

    def test_deserialize_item_key_error(self):
        """It should not Deserialize an item with a KeyError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize an item with a TypeError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, [])

    # ---------------------------------------------------------------------
    #               I T E M  M E T H O D S
    # ---------------------------------------------------------------------

    ######################################################################
    #  TEST ADD ORDER ITEMS
    ######################################################################
    def test_add_order_item(self):
        """It should Create an order with an item and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        item = ItemFactory(order=order)
        order.items.append(item)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.items), 1)
        self.assertEqual(new_order.items[0].product_id, item.product_id)
        self.assertEqual(new_order.items[0].quantity, item.quantity)
        self.assertEqual(new_order.items[0].total, item.total)

        item2 = ItemFactory(order=order)
        order.items.append(item2)
        order.update()

        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.items), 2)
        self.assertEqual(new_order.items[1].product_id, item2.product_id)
        self.assertEqual(new_order.items[1].quantity, item2.quantity)
        self.assertEqual(new_order.items[1].total, item2.total)

    def test_list_all_items(self):
        """It should list all items for an order"""
        order = OrderFactory()
        item1 = ItemFactory(order=order)
        order.items.append(item1)
        item2 = ItemFactory(order=order)
        order.items.append(item2)
        item3 = ItemFactory(order=order)
        order.items.append(item3)
        order.create()
        items = Item.all()
        self.assertEqual(len([item for item in items]), 3)

    def test_update_order_item(self):
        """It should update an order item"""
        order = OrderFactory()
        item = ItemFactory(order=order)
        order.items.append(item)
        order.create()

        # modify properties of the item
        new_item = ItemFactory(order=order)
        item.quantity = new_item.quantity
        item.total = new_item.total
        item.product_id = new_item.product_id
        item.update()

        updated_order = Order.find(order.id)
        updated_item = updated_order.items[0]

        self.assertEqual(updated_item.product_id, item.product_id)
        self.assertEqual(updated_item.quantity, new_item.quantity)
        self.assertEqual(updated_item.total, new_item.total)

    def test_delete_order_item(self):
        """It should Delete an orders item"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        item = ItemFactory(order=order)
        order.create()

        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        order = Order.find(order.id)
        item = order.items[0]
        item.delete()
        order.update()

        order = Order.find(order.id)
        self.assertEqual(len(order.items), 0)
