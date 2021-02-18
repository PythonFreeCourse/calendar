import datetime

import pytest

from app.internal.emotion import (
    Emoticon,
    is_emotion_above_significance,
    get_dominant_emotion,
    get_emotion,
    get_html_emoticon)

from app.routers.event import create_event


HAPPY_MESSAGE = "This is great"  # 100% happy
SAD_MESSAGE = "I'm so lonely and feel bad"  # 100% sad
ANGRY_MESSAGE = "I'm so mad, stop it"  # 100% angry
FEAR_MESSAGE = "I'm afraid to fall"  # 100% fear
SURPRISE_MESSAGE = "wow, this is new!"  # 100% surprise


emotion_tests = [
    (HAPPY_MESSAGE, HAPPY_MESSAGE, Emoticon('Happy', 1.0, '&#128515')),
    (SAD_MESSAGE, SAD_MESSAGE, Emoticon('Sad', 1.0, '&#128577')),
    (ANGRY_MESSAGE, ANGRY_MESSAGE, Emoticon('Angry', 1.0, '&#128544')),
    (FEAR_MESSAGE, FEAR_MESSAGE, Emoticon('Fear', 1.0, '&#128561')),
    (SURPRISE_MESSAGE, SURPRISE_MESSAGE,
     Emoticon('Surprise', 1.0, '&#128558')),
    (SURPRISE_MESSAGE, None, Emoticon('Surprise', 1.0, '&#128558')),
    (SURPRISE_MESSAGE, "", Emoticon('Surprise', 1.0, '&#128558')),
    (HAPPY_MESSAGE, SAD_MESSAGE, Emoticon('Happy', 0.6, '&#128515')),
]

emotion_significance_tests = [
    (Emoticon('Happy', 1.0, '&#128515'), None, True),
    (Emoticon('Happy', 0.6, '&#128515'), None, True),
    (Emoticon('Happy', 0.4, '&#128515'), None, False),
    (Emoticon('Happy', 0.4, '&#128515'), 0.3, True),
    (Emoticon('Happy', 0.7, '&#128515'), 0.8, False)
]

get_html_emoticon_tests = [
    (Emoticon('Happy', 1.0, '&#128515'), '&#128515'),
    (Emoticon('Happy', 1.0, None), None)
]

get_emotion_tests = [
    Emoticon(HAPPY_MESSAGE, HAPPY_MESSAGE, '&#128515'),
    Emoticon(SAD_MESSAGE, SAD_MESSAGE, '&#128577'),
    Emoticon(HAPPY_MESSAGE, SAD_MESSAGE, '&#128515'),
    Emoticon(" ", " ", None)
]

create_event_tests = [
    (HAPPY_MESSAGE, datetime.datetime(2019, 5, 21, 0, 0),
     datetime.datetime(2019, 5, 22, 0, 0), False, 1, HAPPY_MESSAGE, "location",
     "&#128515"),
    (SAD_MESSAGE, datetime.datetime(2019, 5, 21, 0, 0),
     datetime.datetime(2019, 5, 22, 0, 0), False, 1, HAPPY_MESSAGE, "location",
     "&#128577"),
    (" ", datetime.datetime(2019, 5, 21, 0, 0),
     datetime.datetime(2019, 5, 22, 0, 0), False, 1, " ", "location",
     None)
]


@pytest.mark.parametrize("title, content, result", emotion_tests)
def test_dominant_emotion(title, content, result):
    assert get_dominant_emotion(title, content) == result


@pytest.mark.parametrize("dominant_emotion, significance, result",
                         emotion_significance_tests)
def test_is_emotion_above_significance(dominant_emotion, significance, result):
    if significance is None:
        assert is_emotion_above_significance(dominant_emotion) == result
    else:
        assert is_emotion_above_significance(dominant_emotion,
                                             significance) == result


@pytest.mark.parametrize("dominant_emotion, result", get_html_emoticon_tests)
def test_get_html_emoticon(dominant_emotion, result):
    assert get_html_emoticon(dominant_emotion) == result


@pytest.mark.parametrize("title, content, result", get_emotion_tests)
def test_get_emotion(title, content, result):
    assert get_emotion(title, content) == result


@pytest.mark.parametrize("title, start, end, all_day, owner_id, content, " +
                         "location, result", create_event_tests)
def test_create_event(title, start, end, all_day,
                      owner_id, content, location, result, session):
    event = create_event(session, title, start,
                         end, all_day, owner_id, content, location)
    assert event.emotion == result
