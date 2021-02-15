from operator import attrgetter
from typing import List

from app.database.models import ShoppingProduct
from app.internal.utils import create_model


def create_shopping_product(db, name, amount, datestr, owner_id) -> ShoppingProduct:
    """Creates and saves a new shopping product."""

    shopping_product = create_model(
        db, ShoppingProduct,
        name=name,
        amount=amount,
        date=datestr,
        owner_id=owner_id,
        is_bought=False
    )
    return shopping_product


def sort_by_date(shopping_products: List[ShoppingProduct]) -> List[ShoppingProduct]:
    """Sorts the products by the product date."""
    temp = shopping_products.copy()
    return sorted(temp, key=attrgetter('datestr'))


def by_id(db, product_id):
    shopping_product = db.query(ShoppingProduct).filter_by(id=product_id).one()
    return shopping_product
