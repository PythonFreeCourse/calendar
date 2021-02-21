from app.routers.audio import router

AUDIO_SETTINGS_URL = router.url_path_for("audio_settings")
GET_CHOICES_URL = router.url_path_for("get_choices")
START_AUDIO_URL = router.url_path_for("start_audio")


def test_get_settings(audio_test_client):
    response = audio_test_client.get(url=AUDIO_SETTINGS_URL)
    assert response.ok
    assert b"Audio Settings" in response.content


def test_start_audio_default(audio_test_client):
    response = audio_test_client.get(START_AUDIO_URL)
    assert response.ok


def test_choices_Off(audio_test_client):
    data = {"music_on": False, "sfx_on": False}
    response = audio_test_client.post(url=GET_CHOICES_URL, data=data)
    assert response.ok


def test_choices_On(audio_test_client):
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


def test_start_audio(audio_test_client):
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


def test_start_audio_sfx_off(audio_test_client):
    data = {"music_on_off": "Off", "sfx_on_off": "Off"}
    audio_test_client.post(url=GET_CHOICES_URL, data=data)
    response = audio_test_client.get(url=START_AUDIO_URL)
    assert response.ok
