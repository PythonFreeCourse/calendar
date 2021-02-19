from datetime import datetime, timedelta
import json
import pytest

from fastapi import HTTPException, Request
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session
from starlette import status


from app.database.models import Comment, Event
from app.dependencies import get_db
from app.internal.utils import delete_instance
from app.main import app

from app.routers import event as evt


CORRECT_EVENT_FORM_DATA = {
    "title": "test title",
    "start_date": "2021-01-28",
    "start_time": "12:59",
    "end_date": "2021-01-28",
    "end_time": "15:01",
    "location": "fake city",
    "vc_link": "https://us02web.zoom.us/j/875384596",
    "description": "content",
    "color": "red",
    "availability": "True",
    "privacy": "public",
    "invited": "a@a.com,b@b.com",
    "event_type": "on",
}

CORRECT_EVENT_FORM_DATA_WITHOUT_EVENT_TYPE = {
    "title": "test title",
    "start_date": "2021-01-28",
    "start_time": "15:59",
    "end_date": "2021-01-27",
    "end_time": "15:01",
    "location_type": "vc_url",
    "location": "https://us02web.zoom.us/j/875384596",
    "description": "content",
    "color": "red",
    "availability": "busy",
    "privacy": "public",
    "event_type": "on",
    "is_google_event": "False",
}

WRONG_EVENT_FORM_DATA = {
    "title": "test title",
    "start_date": "2021-01-28",
    "start_time": "15:59",
    "end_date": "2021-01-27",
    "end_time": "15:01",
    "location": "fake city",
    "vc_link": "not a zoom link",
    "description": "content",
    "color": "red",
    "availability": "True",
    "privacy": "public",
    "invited": "a@a.com,b@b.com",
    "event_type": "on",
    "is_google_event": "False",
}

BAD_EMAILS_FORM_DATA = {
    "title": "test title",
    "start_date": "2021-01-28",
    "start_time": "15:59",
    "end_date": "2021-01-27",
    "end_time": "15:01",
    "location": "fake city",
    "vc_link": "https://us02web.zoom.us/j/875384596",
    "description": "content",
    "color": "red",
    "availability": "busy",
    "privacy": "public",
    "invited": "a@a.com,b@b.com,ccc",
    "event_type": "on",
    "is_google_event": "False",
}

WEEK_LATER_EVENT_FORM_DATA = {
    "title": "test title",
    "start_date": "2021-02-04",
    "start_time": "12:59",
    "end_date": "2021-02-04",
    "end_time": "15:01",
    "location": "fake city",
    "vc_link": "https://us02web.zoom.us/j/875384596",
    "description": "content",
    "color": "red",
    "availability": "busy",
    "privacy": "public",
    "event_type": "on",
    "invited": "a@a.com,b@b.com",
    "is_google_event": "False",
}

TWO_WEEKS_LATER_EVENT_FORM_DATA = {
    "title": "test title",
    "start_date": "2021-02-11",
    "start_time": "12:59",
    "end_date": "2021-02-11",
    "end_time": "15:01",
    "location": "fake city",
    "vc_link": "https://us02web.zoom.us/j/875384596",
    "description": "content",
    "color": "red",
    "availability": "busy",
    "privacy": "public",
    "invited": "a@a.com,b@b.com",
    "event_type": "on",
    "is_google_event": "False",
}

CORRECT_ADD_EVENT_DATA = {
    "title": "test",
    "start": "2021-02-13T09:03:49.560Z",
    "end": "2021-02-13T09:03:49.560Z",
    "content": "test",
    "owner_id": 0,
    "location": "test",
    "is_google_event": "False",
}

NONE_UPDATE_OPTIONS = [
    {},
    {"test": "test"},
]

INVALID_FIELD_UPDATE = [
    {"start": "20.01.2020"},
    {"start": datetime(2020, 2, 2), "end": datetime(2020, 1, 1)},
    {"start": datetime(2030, 2, 2)},
    {"end": datetime(1990, 1, 1)},
]


def test_get_events(event_test_client, session, event):
    response = event_test_client.get("/event/")
    assert response.ok


def test_create_event_api(event_test_client, session, event):
    response = event_test_client.post(
        "/event/",
        data=json.dumps(CORRECT_ADD_EVENT_DATA),
    )
    assert response.ok


def test_eventedit(event_test_client):
    response = event_test_client.get("/event/edit")
    assert response.ok
    assert b"Event Details" in response.content


def test_eventview_with_id(event_test_client, session, event):
    event_id = event.id
    response = event_test_client.get(f"/event/{event_id}")
    assert response.ok
    assert b"Event Details" in response.content


def test_all_day_eventview_with_id(event_test_client, session, all_day_event):
    event_id = all_day_event.id
    response = event_test_client.get(f"/event/{event_id}")
    assert response.ok


def test_create_event_with_default_availability(client, user, session):
    """
    Test create event with default availability. (busy)
    """
    data = {
        "title": "test title",
        "start": datetime.strptime("2021-01-01 15:59", "%Y-%m-%d %H:%M"),
        "end": datetime.strptime("2021-01-02 15:01", "%Y-%m-%d %H:%M"),
        "vc_link": "https://us02web.zoom.us/j/875384596",
        "content": "content",
        "owner_id": user.id,
    }

    event = evt.create_event(session, **data)
    assert event.availability is True


def test_create_event_with_free_availability(client, user, session):
    """
    Test create event with free availability.
    """
    data = {
        "title": "test title",
        "start": datetime.strptime("2021-01-01 15:59", "%Y-%m-%d %H:%M"),
        "end": datetime.strptime("2021-01-02 15:01", "%Y-%m-%d %H:%M"),
        "vc_link": "https://us02web.zoom.us/j/875384596",
        "content": "content",
        "owner_id": user.id,
        "availability": False,
        "is_google_event": False,
    }

    event = evt.create_event(session, **data)
    assert event.availability is False


def test_eventview_without_id(client):
    response = client.get("/event/view")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_eventedit_missing_old_invites(client, user):
    response = client.post(
        client.app.url_path_for("create_new_event"),
        data=CORRECT_EVENT_FORM_DATA,
    )
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND

    different_invitees_event = CORRECT_EVENT_FORM_DATA.copy()
    different_invitees_event["invited"] = "c@c.com,d@d.com"
    response = client.post(
        client.app.url_path_for("create_new_event"),
        data=different_invitees_event,
    )
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND
    for invitee in CORRECT_EVENT_FORM_DATA["invited"].split(","):
        assert invitee in response.headers["location"]


def test_eventedit_bad_emails(client, user):
    response = client.post(
        client.app.url_path_for("create_new_event"),
        data=BAD_EMAILS_FORM_DATA,
    )
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND

    different_invitees_event = CORRECT_EVENT_FORM_DATA.copy()
    different_invitees_event["invited"] = "c@c.com,d@d.com"
    response = client.post(
        client.app.url_path_for("create_new_event"),
        data=different_invitees_event,
    )
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND
    for invitee in CORRECT_EVENT_FORM_DATA["invited"].split(","):
        assert invitee in response.headers["location"]
    assert "ccc" not in response.headers["location"]


def test_eventedit_post_correct(client, user):
    """
    Test create new event successfully.
    """
    response = client.post(
        client.app.url_path_for("create_new_event"),
        data=CORRECT_EVENT_FORM_DATA,
    )
    assert response.ok
    assert (
        client.app.url_path_for("eventview", event_id=1).strip("1")
        in response.headers["location"]
    )


def test_eventedit_post_without_event_type(client, user):
    """
    Test create new event successfully,
    When the event type is not defined by the user.
    """
    response = client.post(
        client.app.url_path_for("create_new_event"),
        data=CORRECT_EVENT_FORM_DATA,
    )
    assert response.status_code == status.HTTP_302_FOUND
    assert (
        client.app.url_path_for("eventview", event_id=1).strip("1")
        in response.headers["location"]
    )


def test_create_event_with_category(client, user, category, session):
    """
    Test create event with category successfully.
    """
    data = {**CORRECT_EVENT_FORM_DATA, **{"category_id": category.id}}

    response = client.post(
        client.app.url_path_for("create_new_event"),
        data=data,
    )
    assert response.ok
    assert (
        client.app.url_path_for("eventview", event_id=1).strip("1")
        in response.headers["location"]
    )


def test_eventedit_post_wrong(client, user):
    """
    Test create new event unsuccessfully.
    """
    response = client.post(
        client.app.url_path_for("create_new_event"),
        data=WRONG_EVENT_FORM_DATA,
    )
    assert response.json()["detail"] == "VC type with no valid zoom link"


def test_eventedit_with_pattern(client, user):
    response = client.post(
        client.app.url_path_for("create_new_event"),
        data=CORRECT_EVENT_FORM_DATA,
    )
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND

    response = client.post(
        client.app.url_path_for("create_new_event"),
        data=WEEK_LATER_EVENT_FORM_DATA,
    )
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND
    assert "Same event happened 1 weeks before too. " in response.headers[
        "location"
    ].replace("+", " ")

    response = client.post(
        client.app.url_path_for("create_new_event"),
        data=TWO_WEEKS_LATER_EVENT_FORM_DATA,
    )
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND
    assert "Same event happened 1 weeks before too. " in response.headers[
        "location"
    ].replace("+", " ")
    assert "Same event happened 2 weeks before too. " in response.headers[
        "location"
    ].replace("+", " ")


@pytest.mark.parametrize("data", NONE_UPDATE_OPTIONS)
def test_invalid_update(event, data, session):
    """
    Test update existing event.
    """
    assert evt.update_event(event_id=event.id, event=data, db=session) is None


@pytest.mark.parametrize("data", INVALID_FIELD_UPDATE)
def test_invalid_fields(event, data, session):
    """
    Test update existing event.
    """
    with pytest.raises(HTTPException):
        response = evt.update_event(event_id=event.id, event=data, db=session)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_not_check_change_dates_allowed(event):
    data = {"start": "20.01.2020"}
    with pytest.raises(HTTPException):
        assert (
            evt.check_change_dates_allowed(event, data).status_code
            == status.HTTP_400_BAD_REQUEST
        )


def test_update_event_availability(event, session):
    """
    Test update event's availability.
    """
    original_availability = event.availability
    data = {"availability": not original_availability}
    assert (
        original_availability
        is not evt.update_event(
            event_id=event.id,
            event=data,
            db=session,
        ).availability
    )


def test_successful_update(event, session):
    """
    Test update existing event successfully.
    """
    data = {
        "title": "successful",
        "start": datetime(2021, 1, 20),
        "end": datetime(2021, 1, 21),
        "availability": "False",
    }
    assert isinstance(evt.update_event(1, data, session), Event)
    updated_event = evt.update_event(event_id=event.id, event=data, db=session)
    assert "successful" in updated_event.title
    assert updated_event.availability is False


def test_update_event_with_category(today_event, category, session):
    """
    Test update category for an existing event successfully.
    """
    data = {
        "title": "successful",
        "category_id": category.id,
    }
    updated_event = evt.update_event(
        event_id=today_event.id,
        event=data,
        db=session,
    )
    assert "successful" in updated_event.title
    assert updated_event.category_id == category.id


def test_update_db_close(event):
    data = {
        "title": "Problem connecting to db in func update_event",
    }
    with pytest.raises(HTTPException):
        assert (
            evt.update_event(
                event_id=event.id,
                event=data,
                db=None,
            ).status_code
            == status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def test_update_event_does_not_exist(event, session):
    data = {"content": "An update test for an event does not exist"}
    with pytest.raises(HTTPException):
        response = evt.update_event(
            event_id=status.HTTP_500_INTERNAL_SERVER_ERROR,
            event=data,
            db=session,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


def test_db_close_update(session, event):
    data = {
        "title": "Problem connecting to db in func _update_event",
    }
    with pytest.raises(HTTPException):
        assert (
            evt._update_event(
                event_id=event.id,
                event_to_update=data,
                db=None,
            ).status_code
            == status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def test_repr(event):
    assert event.__repr__() == f"<Event {event.id}>"


def test_no_connection_to_db_in_delete(event):
    with pytest.raises(HTTPException):
        response = evt.delete_event(event_id=1, db=None)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_no_connection_to_db_in_internal_deletion(event):
    with pytest.raises(HTTPException):
        assert (
            evt._delete_event(event=event, db=None).status_code
            == status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def test_successful_deletion(event_test_client, session, event):
    response = event_test_client.delete("/event/1")
    assert response.ok
    with pytest.raises(HTTPException):
        assert (
            "Event ID does not exist. ID: 1"
            in evt.by_id(db=session, event_id=1).content
        )


def test_change_owner(client, event_test_client, user, session, event):
    """
    Test change owner of an event
    """
    event_id = event.id
    event_details = [
        event.title,
        event.content,
        event.location,
        event.start,
        event.end,
        event.color,
        event.category_id,
    ]
    response = event_test_client.post(f"/event/{event_id}/owner", data=None)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.ok
    assert b"View Event" not in response.content
    for event_detail in event_details:
        assert (
            str(event_detail).encode("utf-8") not in response.content
        ), f"{event_detail} not in view event page"
    data = {"username": "worng_username"}
    response = event_test_client.post(f"/event/{event_id}/owner", data=data)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert b"Username does not exist." in response.content
    data = {"username": user.username}
    response = event_test_client.post(f"/event/{event_id}/owner", data=data)
    assert response.ok
    assert response.status_code == status.HTTP_302_FOUND


def test_deleting_an_event_does_not_exist(event_test_client, event):
    response = event_test_client.delete("/event/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_tamplate_to_share_event(event, session):
    html_template = evt.get_template_to_share_event(
        event_id=1,
        user_name="michael",
        db=session,
        request=Request.get,
    )
    assert html_template is not None


def test_add_comment(
    event_test_client: TestClient,
    session: Session,
    event: Event,
) -> None:
    assert session.query(Comment).first() is None
    content = "test comment"
    path = evt.router.url_path_for("add_comment", event_id=event.id)
    data = {"comment": content}
    response = event_test_client.post(path, data=data, allow_redirects=True)
    assert response.ok
    assert content in response.text
    comment = session.query(Comment).first()
    assert comment
    delete_instance(session, comment)


def test_get_event_data(
    session: Session,
    event: Event,
    comment: Comment,
) -> None:
    data = (
        event,
        [
            {
                "id": 1,
                "avatar": "profile.png",
                "username": "test_username",
                "time": "01/01/2021 00:01",
                "content": "test comment",
            },
        ],
        "%H:%M",
    )
    assert evt.get_event_data(session, event.id) == data


def test_view_comments(
    event_test_client: TestClient,
    event: Event,
    comment: Comment,
) -> None:
    path = evt.router.url_path_for("view_comments", event_id=event.id)
    response = event_test_client.get(path)
    assert response.ok
    assert comment.content in response.text


def test_delete_comment(
    event_test_client: TestClient,
    session: Session,
    event: Event,
    comment: Comment,
) -> None:
    assert session.query(Comment).first()
    path = evt.router.url_path_for("delete_comment")
    data = {
        "event_id": event.id,
        "comment_id": comment.id,
    }
    response = event_test_client.post(path, data=data, allow_redirects=True)
    assert response.ok
    assert "Post Comment" in response.text
    assert session.query(Comment).first() is None


class TestApp:
    client = TestClient(app)
    date_test_data = [datetime.today() - timedelta(1), datetime.today()]
    event_test_data = {
        "title": "Test Title",
        "location": "Fake City",
        "vc_link": "https://us02web.zoom.us/j/875384596",
        "start": date_test_data[0],
        "end": date_test_data[1],
        "content": "Any Words",
        "owner_id": 123,
        "invitees": "user1, user2",
    }

    @staticmethod
    def test_get_db():
        assert isinstance(next(get_db()), Session)

    @staticmethod
    def test_session_db():
        assert get_db() is not None

    @staticmethod
    def check_is_date_before():
        start = TestApp.date_test_data[0]
        end = TestApp.date_test_data[1]
        assert evt.is_date_before(start, end)

    @staticmethod
    def test_bad_check_validation():
        assert not evt.is_date_before(TestApp.date_test_data[0], "bad value")

    @staticmethod
    def test_add_event(session: Session):
        assert evt.add_new_event(TestApp.event_test_data, session) is not None

    @staticmethod
    def test_add_bad_event(session: Session):
        bad_event_test_data = TestApp.event_test_data
        bad_event_test_data["no_colume"] = "some data"
        assert evt.add_new_event(bad_event_test_data, session) is None

    @staticmethod
    def test_add_bad_times_to_event(session: Session):
        bad_event_test_data = TestApp.event_test_data
        bad_event_test_data["start"] = TestApp.date_test_data[1]
        bad_event_test_data["end"] = TestApp.date_test_data[0]
        assert evt.add_new_event(bad_event_test_data, session) is None
