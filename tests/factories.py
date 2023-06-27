import factory
from datetime import date
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Order, Item
import random

class OrderFactory(factory.Factory):
    """Persistent class"""
    class Meta:
        model = Order

    id = factory.Sequence(lambda n: n)
    ## name = factory.Faker("name")
    date = FuzzyDate(date(2008, 1, 1))
    total = round(random.uniform(1.00, 1000.00), 2)
    payment = FuzzyChoice(choices=["CREDITCARD", "DEBITCARD", "VEMO"])
    address = factory.Faker("address")
    customer_id = factory.Faker('random_int', min=10000, max=99999)
    status = FuzzyChoice(choices=["OPEN", "SHIPPING", "DELIVERED", "CANCELLED"])

    @factory.post_generation
    def items(self, create, extracted, **kwargs):   # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted
class ItemFactory(factory.Factory):
    """Creates fake Items"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""
        model = Item

    id = factory.Sequence(lambda n: n)
    product_id = factory.Faker('random_int', min=1, max=100000)
    quantity = factory.Faker('random_int', min=1, max=10)
    total = round(random.uniform(1.00, 100.00), 2)
    order_id = None
    order = factory.SubFactory(OrderFactory)