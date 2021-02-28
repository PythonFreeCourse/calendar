from app.routers.audio import router
from tests.test_login import test_login_successfull

AUDIO_SETTINGS_URL = router.url_path_for("audio_settings")
GET_CHOICES_URL = router.url_path_for("get_choices")
START_AUDIO_URL = router.url_path_for("start_audio")


def test_get_settings(session, audio_test_client):
    test_login_successfull(session, audio_test_client)
    response = audio_test_client.get(url=AUDIO_SETTINGS_URL)
    assert response.ok
    assert b"Audio Settings" in response.content
    assert b"GASTRONOMICA.mp3" in response.content
    assert b"SQUEEK!.mp3" in response.content
    assert b"PHARMACOKINETICS.mp3" in response.content
    assert b"click_1.wav" in response.content
    assert b"click_2.wav" in response.content
    assert b"click_3.wav" in response.content
    assert b"click_4.wav" in response.content


def test_start_audio_default(session, audio_test_client):
    test_login_successfull(session, audio_test_client)
    response = audio_test_client.get(START_AUDIO_URL)
    assert response.ok


def test_choices_Off(session, audio_test_client):
    test_get_settings(session, audio_test_client)
    test_login_successfull(session, audio_test_client)
    data = {"music_on": False, "sfx_on": False}
    response = audio_test_client.post(url=GET_CHOICES_URL, data=data)
    assert response.ok


def test_choices_On(session, audio_test_client):
    test_get_settings(session, audio_test_client)
    test_login_successfull(session, audio_test_client)
    data = {
        "music_on": True,
        "music_choices": ["GASTRONOMICA.mp3"],
        "music_vol": 50,
        "sfx_on": True,
        "sfx_choice": "click_1.wav",
        "sfx_vol": 50,
    }
    response = audio_test_client.post(url=GET_CHOICES_URL, data=data)
    assert response.ok


def test_changing_choices(session, audio_test_client):
    test_get_settings(session, audio_test_client)
    test_login_successfull(session, audio_test_client)
    test_choices_On(session, audio_test_client)
    data = {
        "music_on": True,
        "music_choices": ["SQUEEK!.mp3"],
        "music_vol": 15,
        "sfx_on": True,
        "sfx_choice": "click_2.wav",
        "sfx_vol": 100,
    }
    response = audio_test_client.post(url=GET_CHOICES_URL, data=data)
    assert response.ok


def test_just_music_on(session, audio_test_client):
    test_get_settings(session, audio_test_client)
    test_login_successfull(session, audio_test_client)
    data = {
        "music_on": True,
        "music_choices": ["PHARMACOKINETICS.mp3"],
        "music_vol": 75,
        "sfx_on": False,
    }
    response = audio_test_client.post(url=GET_CHOICES_URL, data=data)
    assert response.ok


def test_just_sfx_on(session, audio_test_client):
    test_get_settings(session, audio_test_client)
    test_login_successfull(session, audio_test_client)
    data = {
        "music_on": False,
        "sfx_on": True,
        "sfx_choice": "click_3.wav",
        "sfx_vol": 20,
    }
    response = audio_test_client.post(url=GET_CHOICES_URL, data=data)
    assert response.ok


def test_start_audio(session, audio_test_client):
    test_get_settings(session, audio_test_client)
    test_login_successfull(session, audio_test_client)
    data = {
        "music_on": True,
        "music_choices": ["GASTRONOMICA.mp3"],
        "music_vol": 50,
        "sfx_on": True,
        "sfx_choice": "click_1.wav",
        "sfx_vol": 50,
    }
    audio_test_client.post(url=GET_CHOICES_URL, data=data)
    response = audio_test_client.get(url=START_AUDIO_URL)
    assert response.ok


def test_start_audio_sfx_off(session, audio_test_client):
    test_get_settings(session, audio_test_client)
    test_login_successfull(session, audio_test_client)
    data = {"music_on_off": "Off", "sfx_on_off": "Off"}
    audio_test_client.post(url=GET_CHOICES_URL, data=data)
    response = audio_test_client.get(url=START_AUDIO_URL)
    assert response.ok
