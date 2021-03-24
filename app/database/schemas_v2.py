"""Pydantic schema models."""
from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, EmailStr, Field, HttpUrl, SecretStr, validator

from app.database import models_v2
from app.internal.privacy import PrivacyKinds


class EventBase(BaseModel):
    """Base Event schema model. Should not be used directly."""

    title: str = Field(
        description=models_v2.Event.title.__doc__,
        example="A title of an event",
    )

    owner_id: int = Field(
        description=models_v2.Event.owner_id.__doc__,
        example=1,
    )

    datetime_start: datetime = Field(
        description=models_v2.Event.datetime_start.__doc__,
        example="2021-03-18 13:00:00",
    )

    datetime_end: datetime = Field(
        description=models_v2.Event.datetime_end.__doc__,
        example="2021-03-18 14:00:00",
    )

    is_all_day: bool = Field(
        description=models_v2.Event.is_all_day.__doc__,
        example=False,
    )

    class Config:  # noqa
        orm_mode = True
        validate_assignment = True


class EventCreate(EventBase):
    """Event schema used for entity creation.

    Extends :class:`EventBase` with event creation information.
    """

    color: str = Field(
        description=models_v2.Event.color.__doc__,
        example="Red",
    )

    content: str = Field(
        description=models_v2.Event.content.__doc__,
        example="The event's content",
    )

    emotion: str = Field(
        description=models_v2.Event.emotion.__doc__,
        example="",
    )

    image: str = Field(
        description=models_v2.Event.image.__doc__,
        example="event_image.png",
    )

    invited_emails: str = Field(
        description=models_v2.Event.invited_emails.__doc__,
        example="invite1@gmail.com, invite2@gmail.com",
    )

    is_available: bool = Field(
        description=models_v2.Event.is_available.__doc__,
        example=False,
    )

    is_google_event: bool = Field(
        description=models_v2.Event.is_google_event.__doc__,
        example=False,
    )

    latitude: float = Field(
        description=models_v2.Event.latitude.__doc__,
        example="32.0853",
    )

    location: str = Field(
        description=models_v2.Event.location.__doc__,
        example="Tel Aviv",
    )

    longitude: float = Field(
        description=models_v2.Event.longitude.__doc__,
        example="34.7818",
    )

    privacy: PrivacyKinds = Field(
        description=models_v2.Event.privacy.__doc__,
        example="PrivacyKinds.Public",
    )

    video_chat_link: HttpUrl = Field(
        description=models_v2.Event.video_chat_link.__doc__,
        example="https://www.link.com",
    )


class Event(EventBase):
    """Event schema used for general use.

    Extends :class:`EventBase` with standard-use event information.
    """

    id: int = Field(
        allow_mutation=False,
        description=models_v2.Event.id.__doc__,
        example=1,
    )


class EventAll(EventCreate, Event):
    """Event schema used for full updates.

    Extends :class:`Event` and :class:`EventCreate.
    """

    pass


class Language(BaseModel):
    """Language schema model."""

    id: int = Field(
        description=models_v2.Language.id.__doc__,
        example=1,
    )

    name: str = Field(
        description=models_v2.Language.name.__doc__,
        example="English",
    )

    code: str = Field(
        description=models_v2.Language.code.__doc__,
        example="en",
    )

    class Config:  # noqa
        orm_mode = True


class UserBase(BaseModel):
    """Base User schema model. Should not be used directly."""

    username: str = Field(
        min_length=3,
        max_length=20,
        regex="^[a-zA-Z0-9_]+$",
        description=models_v2.User.username.__doc__,
        example="user4",
    )

    full_name: str = Field(
        min_length=2,
        description=models_v2.User.full_name.__doc__,
        example="John Locke",
    )

    class Config:  # noqa
        validate_assignment = True


class UserCreate(UserBase):
    """User schema used for entity creation.

    Extends :class:`UserBase` with user registration information."""

    password: SecretStr = Field(
        min_length=3,
        max_length=20,
        description="The user's password.",
        example="L108JL!",
    )

    confirm_password: SecretStr = Field(
        description="Re-entry of the user's password for validation.",
        example="L108JL!",
    )

    email: EmailStr = Field(
        description=models_v2.User.email.__doc__,
        example="user@gmail.com",
    )

    @validator("confirm_password")
    def passwords_match(
        cls,
        confirm_password: SecretStr,
        values: Dict[str, Any],
    ) -> SecretStr:
        """Validates the user correctly re-entered their password.

        Args:
            confirm_password: The re-entered password.
            values: All class field values.

        Returns:
            The re-entered password.

        Raises:
            ValueError if the passwords do not match.
        """
        if "password" in values and confirm_password != values["password"]:
            raise ValueError("Passwords do not match")
        return confirm_password

    class Config:  # noqa
        orm_mode = True


class User(UserBase):
    """User schema used for general use.

    Extends :class:`UserBase` with standard-use user information.
    """

    id: int = Field(
        allow_mutation=False,
        description=models_v2.User.id.__doc__,
        example=1,
    )

    class Config:  # noqa
        orm_mode = True
