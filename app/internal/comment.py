import datetime
from typing import Dict, List

from sqlalchemy.orm.session import Session

from app.database.models import Comment, Event
from app.internal import utils


def create_comment(session: Session, event: Event, content: str) -> int:
    data = {
        'user': utils.get_current_user(),
        'event': event,
        'content': content,
        'time': datetime.datetime.now()
    }
    utils.create_model(session, Comment, **data)


def parse_comment(session: Session, comment: Comment) -> Dict[str, str]:
    user = utils.get_user(session, comment.user_id)
    return {
        'avatar': user.avatar,
        'username': user.username,
        'time': comment.time.strftime(r'%Y/%m/%d %H:%M'),
        'content': comment.content
    }


def display_comments(session: Session, event: Event) -> List[Dict[str, str]]:
    comments = session.query(Comment).filter_by(event_id=event.id).all()
    return [parse_comment(comment) for comment in comments]
