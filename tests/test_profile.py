import os

from fastapi import status
from PIL import Image
import pytest

from app import config
from app.dependencies import MEDIA_PATH
from app.routers.profile import get_image_crop_area, get_placeholder_user

CROP_RESULTS = [
    (20, 10, (5, 0, 15, 10)),
    (10, 20, (0, 5, 10, 15)),
    (10, 10, (0, 0, 10, 10))
]


def test_get_placeholder_user():
    user = get_placeholder_user()
    assert user.username == 'new_user'
    assert user.email == 'my@email.po'
    assert user.password == '1a2s3d4f5g6'
    assert user.full_name == 'My Name'


@pytest.mark.parametrize('width, height, result', CROP_RESULTS)
def test_get_image_crop_area(width, height, result):
    assert get_image_crop_area(width, height) == result


def test_profile_page(profile_test_client):
    profile = profile_test_client.get('/profile')
    data = profile.content
    assert profile.ok
    assert b'profile.png' in data
    assert b'FakeName' in data
    assert b'Happy new user!' in data
    assert b'On This Day' in data


def test_update_user_fullname(profile_test_client):
    new_name_data = {
        'fullname': 'Peter'
    }
    # Get profile page and initialize database
    profile = profile_test_client.get('/profile')

    # Post new data
    profile = profile_test_client.post(
        '/profile/update_user_fullname', data=new_name_data)
    assert profile.status_code == status.HTTP_302_FOUND

    # Get updated data
    data = profile_test_client.get('/profile').content
    assert b'Peter' in data


def test_update_user_email(profile_test_client):
    new_email = {
        'email': 'very@new.email'
    }
    # Get profile page and initialize database
    profile = profile_test_client.get('/profile')

    # Post new data
    profile = profile_test_client.post(
        '/profile/update_user_email', data=new_email)
    assert profile.status_code == status.HTTP_302_FOUND

    # Get updated data
    data = profile_test_client.get('/profile').content
    assert b'very@new.email' in data


def test_update_user_description(profile_test_client):
    new_description = {
        'description': "FastAPI Developer"
    }
    # Get profile page and initialize database
    profile = profile_test_client.get('/profile')

    # Post new data
    profile = profile_test_client.post(
        '/profile/update_user_description', data=new_description)
    assert profile.status_code == status.HTTP_302_FOUND

    # Get updated data
    data = profile_test_client.get('/profile').content
    assert b"FastAPI Developer" in data


def test_update_telegram_id(profile_test_client):
    new_telegram_id = {
        'telegram_id': "12345"
    }
    # Get profile page and initialize database
    profile = profile_test_client.get('/profile')

    # Post new data
    profile = profile_test_client.post(
        '/profile/update_telegram_id', data=new_telegram_id)
    assert profile.status_code == status.HTTP_302_FOUND

    # Get updated data
    data = profile_test_client.get('/profile').content
    assert b"12345" in data


def test_upload_user_photo(profile_test_client):
    example_new_photo = f"{MEDIA_PATH}/example.png"

    # Get profile page and initialize database
    profile = profile_test_client.get('/profile')

    # Post new data
    profile = profile_test_client.post(
        '/profile/upload_user_photo',
        files={'file': (
            "filename", open(example_new_photo, "rb"), "image/png")})
    assert profile.status_code == status.HTTP_302_FOUND

    # Validate new picture saved in media directory
    assert 'fake_user.png' in os.listdir(MEDIA_PATH)

    # Validate new picture size
    new_avatar_path = os.path.join(MEDIA_PATH, 'fake_user.png')
    assert Image.open(new_avatar_path).size == config.AVATAR_SIZE
    os.remove(new_avatar_path)


def test_update_calendar_privacy(profile_test_client):
    new_privacy = {
        'privacy': "Public"
    }
    # Get profile page and initialize database
    profile = profile_test_client.get('/profile')

    # Post new data
    profile = profile_test_client.post(
        '/profile/privacy', data=new_privacy)
    assert profile.status_code == status.HTTP_302_FOUND

    # Get updated data
    data = profile_test_client.get('/profile').content
    assert b"Public" in data
