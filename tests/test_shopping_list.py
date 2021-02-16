import json
from datetime import date, time

import pytest
from sqlalchemy.orm.exc import NoResultFound

from app.database.models import User, ShoppingProduct
from app.internal.create_shopping_list import by_id
from app.internal.utils import create_model, delete_instance

DATE = date(2021, 2, 2)


@pytest.fixture
def shopping_product(session, test1):
    shopping_product_example = create_model(
        session, ShoppingProduct, name="Test", amount=5,
        is_bought=False, date=DATE, owner_id=1, owner=test1
    )
    yield shopping_product_example
    delete_instance(session, shopping_product_example)


@pytest.fixture
def test1(session):
    user_example = create_model(
        session, User, username="test_username", email="testtodo@gmail.com",
        password="123456", full_name="My test", language_id=1
    )
    yield user_example
    delete_instance(session, user_example)


def test_if_product_deleted(
        home_test_client,
        product: ShoppingProduct,
        session):
    response = home_test_client.post(
        "/shopping_product/delete",
        data={"shopping_product_id": product.id}
    )
    assert response.status_code == 302
    with pytest.raises(NoResultFound):
        by_id(session, product.id)


def test_if_product_created(home_test_client, session,
                            product: ShoppingProduct, test1):
    response = home_test_client.post(
        "/shopping_product/add",
        data={"name": product.name,
              "amount": product.amount,
              "datestr": product.date.strftime('%Y-%m-%d'),
              "session": session}
    )
    assert response.status_code == 303
    shopping_product_example = by_id(session, product.id)
    assert product == shopping_product_example


def test_if_product_edited(home_test_client,
                           session,
                           product: ShoppingProduct):
    response = home_test_client.post(
        "/shopping_product/edit",
        data={"task_id": product.id,
              "name": product.name,
              "amount": product.amount,
              "datestr": product.date.strftime('%Y-%m-%d'),
              "session": session}
    )
    assert response.status_code == 303
    shopping_product_example = by_id(session, product.id)
    assert product.name == shopping_product_example.name
    assert product.amount == shopping_product_example.amount


def test_if_product_has_bought(home_test_client,
                               session,
                               product: ShoppingProduct):
    response = home_test_client.post(
        f"/shopping_product/setBought/{product.id}",
        data={"shopping_product_id": product.id}
    )
    assert response.status_code == 303
    response = home_test_client.get(
        f"/shopping_product/{product.id}", data={}
    )
    content = response.content.decode('utf-8')
    content = json.loads(content)
    assert content['is_bought'] is True


def test_if_product_has_not_bought(home_test_client,
                                   session,
                                   product: ShoppingProduct):
    response = home_test_client.post(
        f"/shopping_product/setUnBought/{product.id}",
        data={"shopping_product_id": product.id,
              "session": session}
    )
    assert response.status_code == 303
    response = home_test_client.get(
        f"/shopping_product/{shopping_product.id}", data={}
    )
    content = response.content.decode('utf-8')
    content = json.loads(content)
    assert content['is_bought'] is False
