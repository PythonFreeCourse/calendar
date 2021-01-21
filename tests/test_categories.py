import pytest
from starlette import status
from starlette.datastructures import ImmutableMultiDict

from app.database.models import Event
from app.routers.categories import get_user_categories, validate_request_params


class TestCategories:
    CATEGORY_ALREADY_EXISTS_MESSAGE = "category is already exists for {0} user."
    UNALLOWED_PARAMS = "contains unallowed params"

    @staticmethod
    def test_creating_new_category(client, user):
        response = client.post("/categories/", json={"user_id": user.id, "name": "Foo", "color": "eecc11"})
        assert response.status_code == status.HTTP_200_OK
        assert {"user_id": user.id, "name": "Foo", "color": "eecc11"}.items() <= response.json()['category'].items()

    @staticmethod
    def test_creating_not_unique_category_failed(client, user, category):
        response = client.post("/categories/", json={"user_id": user.id, "name": "Guitar Lesson", "color": "121212"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == TestCategories.CATEGORY_ALREADY_EXISTS_MESSAGE.format(user.id)

    @staticmethod
    def test_create_event_with_category(category):
        event = Event(title="OOO", content="Guitar rocks!!", owner_id=category.user_id, category_id=category.id)
        assert event.category_id is not None
        assert event.category_id == category.id

    @staticmethod
    def test_get_user_categories(client, category):
        response = client.get(f"/categories/?user_id={category.user_id}&name={category.name}&color={category.color}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {"user_id": category.user_id, "color": "121212", "name": "Guitar Lesson", "id": category.id}]

    @staticmethod
    def test_get_category_by_name(client, user, category):
        response = client.get(f"/categories/?user_id={category.user_id}&name={category.name}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {"user_id": category.user_id, "color": "121212", "name": "Guitar Lesson", "id": category.id}]

    @staticmethod
    def test_get_category_by_color(client, user, category):
        response = client.get(f"/categories/?user_id={category.user_id}&color={category.color}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {"user_id": category.user_id, "color": "121212", "name": "Guitar Lesson", "id": category.id}]

    @staticmethod
    def test_get_category_bad_request(client):
        response = client.get(f"/categories/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert TestCategories.UNALLOWED_PARAMS in response.json()["detail"]

    @staticmethod
    def test_repr(category):
        assert category.__repr__() == f'<Category {category.id} {category.name} {category.color}>'

    @staticmethod
    def test_to_dict(category):
        assert {c.name: getattr(category, c.name) for c in category.__table__.columns} == category.to_dict()

    @staticmethod
    def test_get_categories_logic_succeeded(session, user, category):
        assert get_user_categories(session, category.user_id) == [category]

    @staticmethod
    @pytest.mark.parametrize('params, expected_result', [
        (ImmutableMultiDict([('user_id', ''), ('name', ''), ('color', '')]), True),
        (ImmutableMultiDict([('user_id', ''), ('name', '')]), True),
        (ImmutableMultiDict([('user_id', ''), ('color', '')]), True),
        (ImmutableMultiDict([('user_id', '')]), True),
        (ImmutableMultiDict([('name', ''), ('color', '')]), False),
        (ImmutableMultiDict([]), False),
        (ImmutableMultiDict([('user_id', ''), ('name', ''), ('color', ''), ('bad_param', '')]), False),
    ])
    def test_validate_request_params(params, expected_result):
        assert validate_request_params(params) == expected_result
