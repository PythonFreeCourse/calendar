"""CRUD functions for the Event model."""
from typing import List, Optional, Union

from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from app.database.crud import crud
from app.database.crud import user as user_crud
from app.database.models_v2 import Event as EventOrm
from app.database.models_v2 import User as UserOrm
from app.database.schemas_v2 import Event, EventAll, EventCreate, User
from app.internal.privacy import PrivacyKinds


def create(session: Session, event: EventCreate) -> Optional[Event]:
    """Returns an Event after creating and saving a model in the database.

    Args:
        session: The database connection.
        event: The created event data.

    Returns:
        The created Event if successful, otherwise returns None.
    """
    event_orm = EventOrm(**event.dict())
    event_created = crud.insert(session, event_orm)
    if not event_created:
        return None

    event_orm.members.append(event_orm.owner)
    session.commit()
    return Event.from_orm(event_orm)


def delete(session: Session, event: Event) -> bool:
    """Deletes an Event from the database.

    Args:
        session: The database connection.
        event: The Event to delete.

    Returns:
        True if successful, otherwise returns False.
    """
    event_orm = _get_by_id(session, event.id, False)
    if event_orm:
        return crud.delete(session, event_orm)
    return False


def get_database_event_by_id(
    session: Session,
    event_id: int,
) -> Optional[EventOrm]:
    """Returns an Event database model by an ID.

    Args:
        session: The database connection.
        event_id: The Event's ID.

    Returns:
        An Event database model if successful, otherwise returns None.
    """
    event = _get_by_id(session, event_id, False)
    if isinstance(event, EventOrm):
        return event
    return None


def get_by_id(session: Session, event_id: int) -> Optional[Event]:
    """Returns an Event by an ID.

    Args:
        session: The database connection.
        event_id: The Event's ID.

    Returns:
        An Event if successful, otherwise returns None.
    """
    return _get_by_id(session, event_id, True)


def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Event]:
    """Returns all Events.

    TODO: should the return value be limited to public events?

    Args:
        session: The database connection.
        skip: The starting index.
            Defaults to 0.
        limit: The amount of returned items.
            Defaults to 100.

    Returns:
        A list of Events.
    """
    events = crud.get_all_database_models(session, EventOrm, skip, limit)
    return parse_obj_as(List[Event], events)


def update_event(session: Session, event: EventAll) -> bool:
    """Updates an Event's data in a complete update.

    Args:
        session: The database connection.
        event: The Event to update.

    Returns:
        True if successful, otherwise returns False.
    """
    return crud.update_database_by_schema_model(
        session,
        event.id,
        event,
        EventOrm,
    )


def get_members(session: Session, event: Event) -> List[User]:
    """Returns a list of the events User members.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        A list of Users.
    """
    event_orm = _get_by_id(session, event.id, False)
    if isinstance(event_orm, EventOrm):
        return parse_obj_as(List[User], event_orm.members)
    return []


def add_member(session: Session, event: Event, user: User) -> bool:
    """Adds a User to an event.

    Args:
        session: The database connection.
        event: The Event to update.
        user: The User being added to the Event.

    Returns:
        True if successful, otherwise returns False.
    """
    user_orm = user_crud.get_database_user_by_id(session, user.id)
    event_orm = _get_by_id(session, event.id, False)
    if isinstance(event_orm, EventOrm):
        event_orm.members.append(user_orm)
        session.commit()
        return True
    return False


def remove_member(session: Session, event: Event, user: User) -> bool:
    """Removes a User from an event.

    Args:
        session: The database connection.
        event: The Event to update.
        user: The User being added to the Event.

    Returns:
        True if successful, otherwise returns False.
    """
    user_orm = user_crud.get_database_user_by_id(session, user.id)
    event_orm = _get_by_id(session, event.id, False)
    if isinstance(event_orm, EventOrm):
        event_orm.members.remove(user_orm)
        session.commit()
        return True
    return False


# TODO: function
# def get_category(session: Session, event: Event) -> Optional[Category]:
#     """Returns the Category the Event belongs to.
#
#     Args:
#         session: The database connection.
#         event: The Event whose data is retrieved.
#
#     Returns:
#         The Category the Event belongs to if found.
#     """
#     event_orm = _get_by_id(session, event.id, False)
#     if event_orm:
#         return Category.from_orm(event_orm.category)
#     return None


def get_color(session: Session, event: Event) -> Optional[str]:
    """Returns the Event's color.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's color, if found.
    """
    return crud.get_property(session, event.id, EventOrm.color)


def get_content(session: Session, event: Event) -> Optional[str]:
    """Returns the Event's content.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's content, if found.
    """
    return crud.get_property(session, event.id, EventOrm.content)


def get_emotion(session: Session, event: Event) -> Optional[str]:
    """Returns the Event's emotion.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's emotion, if found.
    """
    return crud.get_property(session, event.id, EventOrm.emotion)


def get_image(session: Session, event: Event) -> Optional[str]:
    """Returns the Event's image.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's image, if found.
    """
    return crud.get_property(session, event.id, EventOrm.image)


def get_invited_emails(session: Session, event: Event) -> Optional[str]:
    """Returns the a list of emails that have been sent invites to the event.

    TODO: current format returns a single list, should probably be refactored.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        A list of emails in a single string, if found.
    """
    return crud.get_property(session, event.id, EventOrm.invited_emails)


def is_all_day(session: Session, event: Event) -> Optional[bool]:
    """Returns whether the Event is a full day event or not.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's all day status, if found.
    """
    return crud.get_property(session, event.id, EventOrm.is_all_day)


def is_available(session: Session, event: Event) -> Optional[bool]:
    """TODO: This is not an event data but a user data that shows on the event.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's availability status, if found.
    """
    return crud.get_property(session, event.id, EventOrm.is_available)


def is_google_event(session: Session, event: Event) -> Optional[bool]:
    """Returns whether the Event was imported from Google Calendar or not.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's calendar status, if found.
    """
    return crud.get_property(session, event.id, EventOrm.is_google_event)


def get_latitude(session: Session, event: Event) -> Optional[float]:
    """Returns the Event's location's latitude.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's location's latitude, if found.
    """
    return crud.get_property(session, event.id, EventOrm.latitude)


def get_location(session: Session, event: Event) -> Optional[str]:
    """Returns the Event's location's address.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's location's address, if found.
    """
    return crud.get_property(session, event.id, EventOrm.location)


def get_longitude(session: Session, event: Event) -> Optional[float]:
    """Returns the Event's location's longitude.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's location's longitude, if found.
    """
    return crud.get_property(session, event.id, EventOrm.longitude)


def get_owner(session: Session, event: Event) -> Optional[User]:
    """Returns the Event's owner.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The User who created the event, if found.
    """
    event_orm = _get_by_id(session, event.id, False)
    if isinstance(event_orm, EventOrm):
        return User.from_orm(event_orm.owner)
    return None


def change_owner(session: Session, event: Event, user_id: int) -> bool:
    """Sets a new owner for an Event.

    Args:
        session: The database connection.
        event: The Event to update.
        user_id: The new owner's user ID.

    Returns:
        True if successful, otherwise returns False.
    """
    event_orm = _get_by_id(session, event.id, False)
    new_owner = user_crud.get_database_user_by_id(session, user_id)
    if not isinstance(event_orm, EventOrm) or not isinstance(
        new_owner,
        UserOrm,
    ):
        return False

    event_orm.owner = new_owner

    # TODO: The flow of changing owners isn't clear.
    #  If the owner must be a member of a group than this might not be needed.
    event_orm.members.append(new_owner)
    session.commit()
    return True


def get_privacy(session: Session, event: Event) -> Optional[PrivacyKinds]:
    """Returns the Event's privacy setting.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's privacy setting, if found.
    """
    return crud.get_property(session, event.id, EventOrm.privacy)


def get_video_chat_link(session: Session, event: Event) -> Optional[str]:
    """Returns the Event's video chat link.

    Args:
        session: The database connection.
        event: The Event whose data is retrieved.

    Returns:
        The Event's video chat link, if found.
    """
    return crud.get_property(session, event.id, EventOrm.video_chat_link)


def _get_by_id(
    session: Session,
    event_id: int,
    to_schema: bool,
) -> Optional[Union[Event, EventOrm]]:
    """Returns an Event schema or database model by an ID.

    Args:
        session: The database connection.
        event_id: The event's ID.
        to_schema: Whether to convert to schema.
            Defaults to True.

    Returns:
        An Event schema or database model, as requested, if successful,
        otherwise returns None.
    """
    keywords = {EventOrm.id.key: event_id}
    return _get_by_parameter(session, to_schema, **keywords)


def _get_by_parameter(
    session: Session, to_schema: bool = True, **kwargs
) -> Optional[Union[Event, EventOrm]]:
    """Returns an Event by a parameter.

    Args:
        session: The database connection.
        to_schema: Whether to convert to schema.
            Defaults to True.
        **kwargs: The parameter to filter by.
            Must be in the format of: key=value.

    Returns:
        An Event schema or database model, as requested, if successful,
        otherwise returns None.
    """
    event = crud.get_database_model_by_parameter(session, EventOrm, **kwargs)
    if isinstance(event, EventOrm):
        if to_schema:
            return Event.from_orm(event)
        else:
            return event
    else:
        return None
