from app.routers.audio import get_user, on_click
from pygame import mixer
from pynput.mouse import Button

OK = 200
REDIRECT = 302


def test_get_settings(audio_test_client):
    response = audio_test_client.get("/audio-settings/")
    assert response.status_code == OK
    assert b"Audio Settings" in response.content


def test_start_audio_default(audio_test_client):
    response = audio_test_client.get("/start_audio/")
    assert response.status_code == OK


def test_stop_audio_default(audio_test_client):
    response = audio_test_client.get("/stop_audio/")
    assert response.status_code == OK


def test_choices_Off(audio_test_client):
    response = audio_test_client.post("/audio-settings/", data={
        "music_on_off": "Off", "sfx_on_off": "Off"
    })
    assert response.status_code == REDIRECT


def test_choices_On(audio_test_client):
    response = audio_test_client.post("/audio-settings/", data={
        "music_on_off": "On", "music_choices": ["GASTRONOMICA.mp3"], "music_vol": 50,
        "sfx_on_off": "On", "sfx_choice": "click 1.wav", "sfx_vol": 50
    })
    assert response.status_code == REDIRECT


def test_start_audio(audio_test_client):   
    mixer.stop()
    audio_test_client.get("/audio-settings/")
    audio_test_client.post("/audio-settings/", data={
        "music_on_off": "On", "music_choices": ["GASTRONOMICA.mp3"], "music_vol": 50,
        "sfx_on_off": "On", "sfx_choice": "click 1.wav", "sfx_vol": 50
    })
    _, _1 = None, None
    on_click(_, _1, Button.left, True)
    response = audio_test_client.get("/start_audio/")
    assert response.status_code == OK


def test_stop_audio(audio_test_client):
    audio_test_client.get("/audio-settings/")
    audio_test_client.get("/start_audio/")
    response = audio_test_client.get("/stop_audio/")
    assert response.status_code == OK


def test_start_audio_sfx_off(audio_test_client):   
    audio_test_client.get("/audio-settings/")
    audio_test_client.post("/audio-settings/", data={
        "music_on_off": "Off", "sfx_on_off": "Off"
    })
    _, _1 = None, None
    response = audio_test_client.get("/start_audio/")
    assert response.status_code == OK


def test_get_user(session, user):
    new_user = get_user(session, "bla", user)
    assert new_user.username == user.username