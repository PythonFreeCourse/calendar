import datetime
import json
from typing import Dict

from sqlalchemy.orm.session import Session

from app.database.models import Comment, Event
from app.internal import utils


def create_comment(session: Session, event: Event, content: str) -> None:
    """Creates a comment instance in the DB.

    Args:
        session (Session): DB session.
        event (Event): Instance of the event to create a comment for.
        content (str): The content of the comment.
    """
    data = {
        'user': utils.get_current_user(session),
        'event': event,
        'content': content,
        'time': datetime.datetime.now()
    }
    utils.create_model(session, Comment, **data)


def parse_comment(session: Session, comment: Comment) -> Dict[str, str]:
    """Returns a dictionary with the comment's info.

    Args:
        session (Session): DB session.
        comment (Comment): Comment instance to parse.

    Returns:
        dict(str: str): Comment's info.
                        'id' - The comment's.
                        'avatar' - Commentor's profile image.
                        'username' - Commentor's username.
                        'time' - Comment's posting time.
                        'content' - Comment's content
    """
    user = utils.get_user(session, comment.user_id)
    return {
        'id': comment.id,
        'avatar': user.avatar,
        'username': user.username,
        'time': comment.time.strftime(r'%d/%m/%Y %H:%M'),
        'content': comment.content
    }


def display_comments(session: Session, event: Event) -> str:
    """Returns a list of info dictionaries of all the comments for the given
    event.

    Args:
        session (Session): DB session.
        event (Event): Event instance to fetch comments for.

    Returns:
        list(dict(str: str)): List of info dictionaries of all the comments for
                              the given event.
    """
    comments = session.query(Comment).filter_by(event_id=event.id).all()
    return json.dumps([parse_comment(session, comment)
                       for comment in comments])


def delete_comment(session: Session, comment_id: int) -> bool:
    """Deletes a comment instance based on `comment_id`. Returns True if
    successful, False otherwise.

    Args:
        session (Session): DB session.
        comment_id (int): ID of comment instance to delete.

    Returns:
        bool: True if successful, False otherwise.
    """
    comment = session.query(Comment).filter_by(id=comment_id).first()
    if comment:
        utils.delete_instance(session, comment)
        return True
    return False
