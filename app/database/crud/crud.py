"""Low level CRUD functions, generalised for wider usage.

Functions listed here should be accessed only from other CRUD modules,
and not directly from the app.
"""
from typing import Any, List, Optional, Type, Union

from pydantic import BaseModel
from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
    OperationalError,
    SQLAlchemyError,
    StatementError,
)
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.exc import UnmappedInstanceError

from app.database.models_v2 import Base
from app.dependencies import logger


def insert(session: Session, instance: Base) -> bool:
    """Inserts a new row into the database.

    Args:
        session: The database connection.
        instance: The object to save.

    Returns:
        True if successful, otherwise returns False.

    Raises:
        SQLAlchemyError: If the database tables were not created.

    """
    if issubclass(instance.__class__, Base):
        try:
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return True
        except IntegrityError as e:
            logger.exception(e)
            return False
        except OperationalError as e:
            logger.exception(e)
            raise SQLAlchemyError("Database tables were not created yet.")
    return False


def delete(session: Session, instance: Base) -> bool:
    """Deletes a row from the database using the database model.

    Args:
        session: The database connection.
        instance: The object to delete.

    Returns:
        True if successful, otherwise returns False.
    """
    return delete_multiple(session, [instance])


def delete_multiple(session: Session, instances: List[Base]) -> bool:
    """Deletes a multiple rows from the database using the database models.

    Args:
        session: The database connection.
        instances: A list of objects to delete.

    Returns:
        True if successful, otherwise returns False.
    """
    try:
        for instance in instances:
            session.delete(instance)
        session.commit()
        return True
    except InvalidRequestError:
        return False
    except UnmappedInstanceError:
        return False


def get_by_id(
    session: Session,
    entity_id: int,
    orm_class: Type[Base],
) -> Optional[Union[BaseModel, Base]]:
    """Returns a schema or database model by an ID.

    Args:
        session: The database connection.
        entity_id: The entity's ID.
        orm_class: The database mapped model class.

    Returns:
        A BaseModel or Base model, as requested, if successful,
        otherwise returns None.
    """
    keywords = {orm_class.id.key: entity_id}
    return get_database_model_by_parameter(session, orm_class, **keywords)


def get_database_model_by_parameter(
    session: Session,
    orm_class: Type[Base],
    **kwargs: Any,
) -> Optional[Union[BaseModel, Base]]:
    """Returns a schema or database model by a parameter.

    Args:
        session: The database connection.
        orm_class: The database mapped model class.
        **kwargs: The parameter to filter by.
            Must be in the format of: key=value.

    Returns:
        A BaseModel or Base model, as requested, if successful,
        otherwise returns None.
    """
    try:
        return session.query(orm_class).filter_by(**kwargs).first()
    except OperationalError as e:
        logger.exception(e)
        return None


def get_all_database_models(
    session: Session,
    orm_class: Type[Base],
    skip: int = 0,
    limit: int = 100,
) -> List[Base]:
    """Returns all models from the database.

    Args:
        session: The database connection.
        orm_class: The database mapped model class.
        skip: The starting index.
            Defaults to 0.
        limit: The amount of returned items.
            Defaults to 100.

    Returns:
        A list database models.
    """
    try:
        return session.query(orm_class).offset(skip).limit(limit).all()
    except OperationalError as e:
        logger.exception(e)
        return []


def get_property(
    session: Session,
    entity_id: int,
    column: InstrumentedAttribute,
) -> Optional[Any]:
    """Returns the value of an entity's property.

    Args:
        session: The database connection.
        entity_id: The entity's ID.
        column: The database column from where to query the data.

    Returns:
        The value of the entity's database column.
    """
    orm_model = get_by_id(session, entity_id, column.class_)
    if not orm_model:
        return None

    return getattr(orm_model, column.key)


def set_property(
    session: Session,
    entity_id: int,
    column: InstrumentedAttribute,
    value: Any,
) -> bool:
    """Sets a new value for an entity's property.

    Args:
        session: The database connection.
        entity_id: The entity's ID.
        column: The database column to where the data is saved.
        value: The new value to set.

    Returns:
        True if successful, otherwise returns False.
    """
    orm_model = get_by_id(session, entity_id, column.class_)
    if not orm_model:
        return False

    setattr(orm_model, column.key, value)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        return False
    except StatementError:
        session.rollback()
        return False
    return True


def update_database_by_schema_model(
    session: Session,
    entity_id: int,
    schema_instance: BaseModel,
    orm_class: Type[Base],
) -> bool:
    """Updates the database model by extracting data from the schema object.

    ID is passed as a separate parameter for instances where an ID is named
    something other than "id".

    Args:
        session: The database connection.
        entity_id: The entity's ID.
        schema_instance: The schema model whose data is used for the update.
        orm_class: The database mapped model class.

    Returns:
        True if successful, otherwise returns False.
    """
    id_filter = {orm_class.id.key: entity_id}
    try:
        (
            session.query(orm_class)
            .filter_by(**id_filter)
            .update(schema_instance.dict())
        )
        session.commit()
        return True
    except InvalidRequestError:
        return False
