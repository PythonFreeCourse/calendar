from typing import List, Union

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models import Invitation


def get_all_invitations(session: Session, **param) -> List[Invitation]:
    """Returns all invitations filter by param."""

    try:
        invitations = list(session.query(Invitation).filter_by(**param))
    except SQLAlchemyError:
        return []
    else:
        return invitations


def get_invitation_by_id(
        invitation_id: int, session: Session
) -> Union[Invitation, None]:
    """Returns a invitation by an id.
    if id does not exist, returns None."""

    return session.query(Invitation).filter_by(id=invitation_id).first()
