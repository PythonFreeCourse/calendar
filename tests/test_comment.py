import json

from sqlalchemy.orm.session import Session

from app.database.models import Comment, Event, User
from app.internal import comment as cmt
from app.internal.utils import delete_instance


def test_create_comment(session: Session, event: Event, user: User) -> None:
    assert session.query(Comment).first() is None
    cmt.create_comment(session, event, 'test content')
    comment = session.query(Comment).first()
    assert comment
    delete_instance(session, comment)


def test_parse_comment(session: Session, comment: Comment) -> None:
    data = {
        'id': 1,
        'avatar': 'profile.png',
        'username': 'test_username',
        'time': '01/01/2021 00:01',
        'content': 'test comment',
    }
    assert cmt.parse_comment(session, comment) == data


def test_display_comment(session: Session, event: Event,
                         comment: Comment) -> None:
    comments = json.loads(cmt.display_comments(session, event))
    assert len(comments) == 1


def test_display_comment_empty(session: Session, event: Event) -> None:
    comments = json.loads(cmt.display_comments(session, event))
    assert comments == []


def test_delete_comment(session: Session, comment: Comment) -> None:
    assert session.query(Comment).first()
    assert cmt.delete_comment(session, comment.id)
    assert session.query(Comment).first() is None
    assert not cmt.delete_comment(session, comment.id)
