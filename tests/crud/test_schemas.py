"""Tests for Pydantic schema models."""
import pytest
from pydantic import SecretStr, ValidationError

from app.database.schemas_v2 import EventAll, EventCreate, Language, UserCreate


class TestUser:
    @staticmethod
    def test_user_create(user_create: UserCreate):
        assert user_create

    USERNAME_ERRORS = [
        "u",
        "usernameusernameusername",
        "username!#$",
    ]

    @staticmethod
    @pytest.mark.parametrize("username", USERNAME_ERRORS)
    def test_user_create_username_errors(
        user_create: UserCreate,
        username: str,
    ):
        with pytest.raises(ValidationError):
            user_create.username = username
            UserCreate(**user_create.dict())

    @staticmethod
    def test_user_create_full_name_errors(user_create: UserCreate):
        with pytest.raises(ValidationError):
            user_create.full_name = "a"
            UserCreate(**user_create.dict())

    PASSWORD_ERRORS = [
        ("p", "p"),
        ("password is very very long", "password is very very long"),
        ("password!#$", "password"),
    ]

    @staticmethod
    @pytest.mark.parametrize("password, confirm", PASSWORD_ERRORS)
    def test_user_create_password_errors(
        user_create: UserCreate,
        password: str,
        confirm: str,
    ):
        with pytest.raises(ValidationError):
            user_create.password = password
            user_create.confirm_password = SecretStr(confirm)
            UserCreate(**user_create.dict())


class TestEvent:
    @staticmethod
    def test_event_create(event_create: EventCreate):
        assert event_create

    @staticmethod
    def test_event_all(event_create: EventCreate):
        event_all = EventAll(**event_create.dict(), id=1)
        assert event_all


class TestLanguage:
    @staticmethod
    def test_language(language: Language):
        assert language
