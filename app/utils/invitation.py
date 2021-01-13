from typing import List

from sqlalchemy.exc import SQLAlchemyError

from app.config import session
from app.database.models import Invitation


def get_all_invitations(**parm) -> List[Invitation]:
    """Returns all invitations filter by parm."""

    try:
        invitations = list(session.query(Invitation).filter_by(**parm))
    except SQLAlchemyError:
        return []
    else:
        return invitations


def get_invitation_by_id(invitation_id: int) -> Invitation:
    """Returns a invitation by an id."""

    return session.query(Invitation).filter_by(id=invitation_id).first()
