"""
Models for Order

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from abc import abstractmethod
from enum import Enum
from datetime import datetime

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Order.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

class ShipmentStatus(Enum):
    """Enumeration of order status"""
    
    OPEN = 0
    SHIPPING = 1
    DELIVERED = 2
    CANCELLED = 3

class PaymentMethods(Enum):
    """Enumeration of order status"""
    
    CREDITCARD = 0
    DEBITCARD = 1
    VEMO = 2

class BaseModel:
    """
    A base class of data model that other order and OrderProduct models can inherit from
    """
    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    @abstractmethod
    def serialize(self):
        """ Convert an object to dictionary """
    
    @abstractmethod
    def deserialize(self, data):
        """ Convert a dictionary to an object """

    def create(self):
        """
        Creates a Order to the database
        """
        logger.info("Creating %s", self.id)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Order to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Order from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Orders in the database """
        logger.info("Processing all Orders")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Order by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Orders with the given name

        Args:
            name (string): the name of the Orders you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

#################################################dwd#
# OrderProduct MODEL
##################################################
class OrderProduct(db.Model, BaseModel):
    """
    A Class that represent OrderProduct Model
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow())
    update_time = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow())
    product_id = db.Column(db.Integer, nullable=False) # should be set as ForeignKey db.ForeignKey('product.id'), but this will give "table not found" error 
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    order_id = db.Column(
        db.Integer, db.ForeignKey("order.id", ondelete="CASCADE"), nullable=False
    )
    
    def serialize(self) -> dict:
        """Serialize an Order into a dict"""
        return {
            "id": self.id,  
            "create_time": self.create_time.isoformat(),
            "update_time": self.update_time.isoformat(),
            "product_id": self.product_id,
            "quantity": self.quantity,
            "total": self.total,
            "order_id": self.order_id,
        }
    def deserialize(self, data: dict):
        """
        Deserializes a Pet from a dictionary
        Args:
            data (dict): A dictionary containing the Pet data
        """
        try:
            self.id = data["id"]
            self.create_time = data["create_time"]
            self.update_time = data["update_time"]
            self.product_id = data["product_id"]
            self.quantity = data["quantity"]
            self.total = data["total"]
            self.order_id = data["total"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError("Invalid pet: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data " + str(error)
            ) from error
        return self

##################################################
# ORDER MODEL
##################################################
class Order(db.Model, BaseModel):
    """
    A Class that represent Order Model
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow())
    update_time = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow())
    total = db.Column(db.Float, nullable=False)
    payment = db.Column(db.Enum(PaymentMethods), nullable=False)
    address = db.Column(db.String(53), nullable = False)
    customer_id = db.Column(db.Integer, nullable=False) # should be set as ForeignKey db.ForeignKey('customer.id'), but this will give "table not found" error 
    status = db.Column(
        db.Enum(ShipmentStatus), nullable=False, server_default=(ShipmentStatus.OPEN.name)
    )
    products = db.relationship("OrderProduct", passive_deletes=True, cascade="delete")  # products will be deleted when order is deleted
    
    def serialize(self) -> dict:
        """Serialize an Order into a dict"""
        order = {
            "id": self.id,
            "create_time": self.create_time.isoformat(),
            "update_time": self.update_time.isoformat(),
            "total": self.total,
            "payment": self.payment.name, # convert enum to string
            "address": self.address,
            "customer_id": self.customer_id,
            "status": self.status.name, # convert enum to string
            "products": []
        }
        for product in self.products:
            order["products"].append(product.serialize())
        return order
     
    def deserialize(self, data: dict):
        """
        Deserializes an Order from a dictionary
        Args:
            data (dict): A dictionary containing the Order data
        """
        try:
            # assert(isinstance(data["total"],float), "total")
            self.id = data["id"]
            self.create_time = datetime.fromisoformat(data["create_time"])
            self.update_time = datetime.fromisoformat(data["update_time"])
            self.total = data["total"]
            self.payment = getattr(PaymentMethods, data["payment"])
            self.customer_id = data["customer_id"]
            self.status = getattr(ShipmentStatus, data["status"])
            products = data["products"]
            for json_product in products:
                product = OrderProduct()
                product.deserialize(json_product)
                self.products.append(product)
        # except AssertionError as error:
        #     raise DataValidationError("Invalid type for boolean [available]: " + str(type(data["available"])))
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError("Invalid order: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data " + str(error)
            ) from error
        return self
