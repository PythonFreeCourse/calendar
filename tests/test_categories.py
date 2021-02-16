import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.testing import mock

from starlette import status
from starlette.datastructures import ImmutableMultiDict

from app.database.models import Event, Category
from app.routers.categories import get_user_categories, validate_request_params


class TestCategories:
    CATEGORY_ALREADY_EXISTS_MSG = b"category already exists"
    CREATE_CATEGORY = b"You have created"
    UNALLOWED_PARAMS = "contains unallowed params"

    @staticmethod
    def test_get_categories_logic_succeeded(session, user, category):
        assert get_user_categories(session, category.user_id) == [category]

    # @staticmethod
    # def test_mocking_constant_a(user, mocker, category, client):
    #     mocker.patch(Category.create, return_value=Category(name='Foo', color='eecc11', user_id=category.user_id))
    #     response = client.post("/categories",
    #                             data={"user_id": user.id,
    #                                     "category": "Foo",
    #                                     "color": "eecc11",})
    #     assert response.ok
    #     assert TestCategories.CREATE_CATEGORY in response.content
    
    @staticmethod
    def test_creating_new_category(session, client, user):
        response = client.post("/for_categories_test",
                               data={"user_id": user.id,
                                     "category": "Foo",
                                     "color": "eecc11",})
        assert response.ok
        assert TestCategories.CREATE_CATEGORY in response.content

    @staticmethod
    def test_creating_not_unique_category_failed(client, sender, category):
        response = client.post("/for_categories_test",
                               data={"category": "Guitar Lesson",
                                     "color": "121212",
                                     "user_id": sender.id})
        assert response.ok
        assert TestCategories.CATEGORY_ALREADY_EXISTS_MSG in response.content

    @staticmethod
    def test_create_event_with_category(category):
        event = Event(title="OOO", content="Guitar rocks!!",
                      owner_id=category.user_id, category_id=category.id)
        assert event.category_id is not None
        assert event.category_id == category.id

    @staticmethod
    def test_update_event_with_category(today_event, category):
        assert today_event.category_id is None
        today_event.category_id = category.id
        assert today_event.category_id is not None
        assert today_event.category_id == category.id

    @staticmethod
    def test_get_user_categories(client, category):
        response = client.get(f"/categories/by_parameters/?"
                              f"user_id={category.user_id}"
                              f"&name={category.name}&color={category.color}")
        assert response.ok
        assert set(response.json()[0].items()) == {
            ("user_id", category.user_id), ("color", "121212"),
            ("name", "Guitar Lesson"), ("id", category.id)}

    @staticmethod
    def test_get_category_by_name(client, sender, category):
        response = client.get(f"/categories/by_parameters/?"
                              f"user_id={category.user_id}"
                              f"&name={category.name}")
        assert response.ok
        assert set(response.json()[0].items()) == {
            ("user_id", category.user_id), ("color", "121212"),
            ("name", "Guitar Lesson"), ("id", category.id)}

    @staticmethod
    def test_get_category_by_color(client, sender, category):
        response = client.get(f"/categories/by_parameters/?"
                              f"user_id={category.user_id}&"
                              f"color={category.color}")
        assert response.ok
        assert set(response.json()[0].items()) == {
            ("user_id", category.user_id), ("color", "121212"),
            ("name", "Guitar Lesson"), ("id", category.id)}

    @staticmethod
    def test_get_category_ok_request(client):
        response = client.get("/categories")
        assert response.ok

    @staticmethod
    def test_repr(category):
        assert category.__repr__() == \
               f'<Category {category.id} {category.name} {category.color}>'

    @staticmethod
    def test_to_dict(category):
        assert {c.name: getattr(category, c.name) for c in
                category.__table__.columns} == category.to_dict()

    @staticmethod
    @pytest.mark.parametrize('params, expected_result', [
        (ImmutableMultiDict([('user_id', ''), ('name', ''),
                             ('color', '')]), True),
        (ImmutableMultiDict([('user_id', ''), ('name', '')]), True),
        (ImmutableMultiDict([('user_id', ''), ('color', '')]), True),
        (ImmutableMultiDict([('user_id', '')]), True),
        (ImmutableMultiDict([('name', ''), ('color', '')]), False),
        (ImmutableMultiDict([]), False),
        (ImmutableMultiDict([('user_id', ''), ('name', ''), ('color', ''),
                             ('bad_param', '')]), False),
    ])
    def test_validate_request_params(params, expected_result):
        assert validate_request_params(params) == expected_result

    @staticmethod
    def test_get_categories_failed(session):
        def raise_error(param):
            raise SQLAlchemyError()

        session.query = mock.Mock(side_effect=raise_error)
        assert get_user_categories(session, 1) == []

    # @staticmethod
    # def test_event_status_ok(client):
    #     response = client.get("/event/edit")
    #     assert response.ok