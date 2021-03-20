"""CRUD functions for the User model."""
from typing import Any, List, Optional, Union

from pydantic import (
    EmailStr,
    SecretStr,
    ValidationError,
    parse_obj_as,
    validate_email,
)
from pydantic.errors import EmailError
from sqlalchemy.orm import Session

from app.database.crud import crud
from app.database.crud.temp_utils import get_hashed_password_v2
from app.database.models_v2 import Event as EventOrm
from app.database.models_v2 import User as UserOrm
from app.database.schemas_v2 import Event, Language, User, UserCreate
from app.dependencies import logger
from app.internal.privacy import PrivacyKinds


def create(session: Session, user: UserCreate) -> Optional[User]:
    """Returns a User after creating and saving a model in the database.

    Args:
        session: The database connection.
        user: The created user's data.

    Returns:
        The created User if successful, otherwise returns None.
    """
    hashed_password = get_hashed_password_v2(user.password)
    user_orm = UserOrm(
        **user.dict(exclude={"confirm_password", "password"}),
        password=hashed_password,
    )
    if crud.insert(session, user_orm):
        return User.from_orm(user_orm)
    return None


def delete(session: Session, user: User) -> bool:
    """Deletes a User from the database.

    Args:
        session: The database connection.
        user: The User to delete.

    Returns:
        True if successful, otherwise returns False.
    """
    user_orm = get_database_user_by_id(session, user.id)
    if user_orm:
        return crud.delete(session, user_orm)
    return False


def get_database_user_by_id(
    session: Session,
    user_id: int,
) -> Optional[UserOrm]:
    """Returns a User database model by an ID.

    Args:
        session: The database connection.
        user_id: The User's ID.

    Returns:
        A User database model if successful, otherwise returns None.
    """
    user = _get_by_id(session, user_id, False)
    if isinstance(user, UserOrm):
        return user
    return None


def get_by_id(session: Session, user_id: int) -> Optional[User]:
    """Returns a User by an ID.

    Args:
        session: The database connection.
        user_id: The User's ID.

    Returns:
        A User if successful, otherwise returns None.
    """
    return _get_by_id(session, user_id, True)


def get_by_username(session: Session, username: str) -> Optional[User]:
    """Returns a User by a username.

    Args:
        session: The database connection.
        username: The User's username.

    Returns:
        A User if successful, otherwise returns None.
    """
    keywords = {UserOrm.username.key: username}
    return _get_by_parameter(session, True, **keywords)


def get_by_email(session: Session, email: str) -> Optional[User]:
    """Returns a User by an email address.

    Args:
        session: The database connection.
        email: The User's email address.

    Returns:
        A User if successful, otherwise returns None.
    """
    keywords = {UserOrm.email.key: email}
    return _get_by_parameter(session, True, **keywords)


def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Returns all registered Users.

    Args:
        session: The database connection.
        skip: The starting index.
            Defaults to 0.
        limit: The amount of returned items.
            Defaults to 100.

    Returns:
        A list of registered Users.
    """
    users = crud.get_all_database_models(session, UserOrm, skip, limit)
    return parse_obj_as(List[User], users)


def get_avatar(session: Session, user: User) -> Optional[str]:
    """Returns the User's avatar image.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

     Returns:
        The User's avatar, if found.
    """
    return crud.get_property(session, user.id, UserOrm.avatar)


def set_avatar(session: Session, user: User, file_name: str) -> bool:
    """Sets a new avatar image for the User.

    Args:
        session: The database connection.
        user: The User to update.
        file_name: The new avatar image file.

    Returns:
        True if successful, otherwise returns False.
    """
    return crud.set_property(session, user.id, UserOrm.avatar, file_name)


def get_description(session: Session, user: User) -> Optional[str]:
    """Returns the User's description.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

    Returns:
        The User's description, if found.
    """
    return crud.get_property(session, user.id, UserOrm.description)


def set_description(session: Session, user: User, description: str) -> bool:
    """Sets a new description for the User.

    Args:
        session: The database connection.
        user: The User to update.
        description: The new description.

    Returns:
        True if successful, otherwise returns False.
    """
    return crud.set_property(
        session,
        user.id,
        UserOrm.description,
        description,
    )


def get_email(session: Session, user: User) -> Optional[str]:
    """Returns the User's email address.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

    Returns:
        The User's email address, if found.
    """
    return crud.get_property(session, user.id, UserOrm.email)


def set_email(session: Session, user: User, email: str) -> bool:
    """Sets a new email address for the User.

    Args:
        session: The database connection.
        user: The User to update.
        email: The new email address.

    Returns:
        True if successful, otherwise returns False.
    """
    try:
        validate_email(email)
    except (TypeError, EmailError):
        return False
    return crud.set_property(session, user.id, UserOrm.email, email)


def set_full_name(session: Session, user: User, full_name: str) -> bool:
    """Sets a new full name for the User.

    Args:
        session: The database connection.
        user: The User to update.
        full_name: The new full name.

    Returns:
        True if successful, otherwise returns False.
    """
    try:
        user.full_name = full_name
    except ValidationError:
        return False
    return crud.set_property(session, user.id, UserOrm.full_name, full_name)


def is_active(session: Session, user: User) -> Optional[bool]:
    """Returns whether the User's account is active or not.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

    Returns:
        The User's account status, if found.
    """
    return crud.get_property(session, user.id, UserOrm.is_active)


def set_active(session: Session, user: User, active: bool) -> bool:
    """Sets a new account status for the User.

    Args:
        session: The database connection.
        user: The User to update.
        active: The new status.

    Returns:
        True if successful, otherwise returns False.
    """
    return crud.set_property(session, user.id, UserOrm.is_active, active)


def is_admin(session: Session, user: User) -> Optional[bool]:
    """Returns whether the User is an admin or not.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

    Returns:
        The User's admin status, if found.
    """
    return crud.get_property(session, user.id, UserOrm.is_admin)


def set_admin(session: Session, user: User, is_user_admin: bool) -> bool:
    """Sets a new admin status for the User.

    Args:
        session: The database connection.
        user: The User to update.
        is_user_admin: The new admin status.

    Returns:
        True if successful, otherwise returns False.
    """
    return crud.set_property(session, user.id, UserOrm.is_admin, is_user_admin)


def get_language(session: Session, user: User) -> Optional[Language]:
    """Returns the User's Language.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

    Returns:
        The User's Language, if found.
    """
    user_orm = get_database_user_by_id(session, user.id)
    if user_orm:
        return Language.from_orm(user_orm.language)
    return None


def set_language(session: Session, user: User, language_id: int) -> bool:
    """Sets a new language ID for the User.

    Args:
        session: The database connection.
        user: The User to update.
        language_id: The new language ID.

    Returns:
        True if successful, otherwise returns False.
    """
    return crud.set_property(
        session,
        user.id,
        UserOrm.language_id,
        language_id,
    )


def set_password(session: Session, user: User, password: SecretStr) -> bool:
    """Sets a new password for the User.

    Args:
        session: The database connection.
        user: The User to update.
        password: An unhashed password.

    Returns:
        True if successful, otherwise returns False.
    """
    try:
        UserCreate(
            **user.dict(),
            # This is needed as SecretStr fails here.
            password=password.get_secret_value(),
            confirm_password=password,
            email=EmailStr("email@gmail.com"),
        )
    except (AttributeError, ValidationError):
        return False

    try:
        hashed_password = get_hashed_password_v2(password)
    except TypeError as e:
        logger.exception(e)
        return False
    return crud.set_property(
        session,
        user.id,
        UserOrm.password,
        hashed_password,
    )


def get_privacy(session: Session, user: User) -> Optional[PrivacyKinds]:
    """Returns the User's privacy setting.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

    Returns:
        The User's privacy setting, if found.
    """
    return crud.get_property(session, user.id, UserOrm.privacy)


def set_privacy(session: Session, user: User, privacy: PrivacyKinds) -> bool:
    """Sets a new privacy setting for the User.

    Args:
        session: The database connection.
        user: The User to update.
        privacy: The new privacy setting.

    Returns:
        True if successful, otherwise returns False.
    """
    return crud.set_property(session, user.id, UserOrm.privacy, privacy)


def get_target_weight(session: Session, user: User) -> Optional[float]:
    """Returns the User's target weight.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

    Returns:
        The User's target weight, if found.
    """
    return crud.get_property(session, user.id, UserOrm.target_weight)


def set_target_weight(session: Session, user: User, weight: float) -> bool:
    """Sets a new target weight for the User.

    Args:
        session: The database connection.
        user: The User to update.
        weight: The target weight.

    Returns:
        True if successful, otherwise returns False.
    """
    return crud.set_property(session, user.id, UserOrm.target_weight, weight)


def get_telegram_id(session: Session, user: User) -> Optional[str]:
    """Returns the User's Telegram ID.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

    Returns:
        The User's Telegram ID, if found.
    """
    return crud.get_property(session, user.id, UserOrm.telegram_id)


def set_telegram_id(session: Session, user: User, telegram_id: str) -> bool:
    """Sets a new Telegram ID for the User.

    Args:
        session: The database connection.
        user: The User to update.
        telegram_id: The User's Telegram ID.

    Returns:
        True if successful, otherwise returns False.
    """
    return crud.set_property(
        session,
        user.id,
        UserOrm.telegram_id,
        telegram_id,
    )


def set_username(session: Session, user: User, username: str) -> bool:
    """Sets a new username for the User.

    Args:
        session: The database connection.
        user: The User to update.
        username: The new username.

    Returns:
        True if successful, otherwise returns False.
    """
    original_username = user.username
    try:
        user.username = username
    except ValidationError:
        return False
    result = crud.set_property(session, user.id, UserOrm.username, username)
    if result is False:
        user.username = original_username
        return False
    return True


def get_events(session: Session, user: User) -> List[Event]:
    """Returns a list of Events the User belongs to.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

    Returns:
        A list of Events.
    """
    user_orm = get_database_user_by_id(session, user.id)
    if user_orm:
        return parse_obj_as(List[Event], user_orm.events)
    return []


def get_owned_events(session: Session, user: User) -> List[Event]:
    """Returns a list of Events the User has created.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

    Returns:
        A list of Events.
    """
    user_orm = get_database_user_by_id(session, user.id)
    if user_orm:
        return parse_obj_as(List[Event], user_orm.owned_events)
    return []


def get_google_calender_events(session: Session, user: User) -> List[EventOrm]:
    """Returns a list of Events imported from Google Calendar.

    Args:
        session: The database connection.
        user: The User whose data is retrieved.

    Returns:
        A list of Events.
    """
    user_orm = get_database_user_by_id(session, user.id)
    if not user_orm:
        return []
    return [event for event in user_orm.events if event.is_google_event]


def delete_all_google_calendar_events(session: Session, user: User) -> bool:
    """Deletes all of a User's imported Google Calendar Events.

    Args:
        session: The database connection.
        user: The User to delete data from.

    Returns:
        True if successful, otherwise returns False.
    """
    events = get_google_calender_events(session, user)
    return crud.delete_multiple(session, events)


def _get_by_id(
    session: Session,
    user_id: int,
    to_schema: bool,
) -> Optional[Union[User, UserOrm]]:
    """Returns a User schema or database model by an ID.

    Args:
        session: The database connection.
        user_id: The user's ID.
        to_schema: Whether to convert to schema.
            Defaults to True.

    Returns:
        A User schema or database model, as requested, if successful,
        otherwise returns None.
    """
    keywords = {UserOrm.id.key: user_id}
    return _get_by_parameter(session, to_schema, **keywords)


def _get_by_parameter(
    session: Session, to_schema: bool = True, **kwargs: Any
) -> Optional[Union[User, UserOrm]]:
    """Returns a User by a parameter.

    Args:
        session: The database connection.
        to_schema: Whether to convert to schema.
            Defaults to True.
        **kwargs: The parameter to filter by.
            Must be in the format of: key=value.

    Returns:
        A User schema or database model, as requested, if successful,
        otherwise returns None.
    """
    user = crud.get_database_model_by_parameter(session, UserOrm, **kwargs)
    if isinstance(user, UserOrm):
        if to_schema:
            return User.from_orm(user)
        else:
            return user
    else:
        return None
