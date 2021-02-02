import datetime
from typing import Dict, List

from app.database import SessionLocal
from app.database.models import Comment, Event
from app.internal import utils


def create_comment(event: Event, content: str) -> int:
    session = SessionLocal()
    data = {
        'user': utils.get_current_user(),
        'event': event,
        'content': content,
        'time': datetime.datetime.now()
    }
    utils.create_model(session, Comment, **data)


def parse_comment(comment: Comment) -> Dict[str, str]:
    user = utils.get_user(comment.user_id)
    return {
        'avatar': user.avatar,
        'username': user.username,
        'time': comment.time.strftime(r'%Y/%m/%d %H:%M'),
        'content': comment.content
    }


def display_comments(event: Event) -> List[Dict[str, str]]:
    session = SessionLocal()
    comments = session.query(Comment).filter_by(event_id=event.id).all()
    return [parse_comment(comment) for comment in comments]
