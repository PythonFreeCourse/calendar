from fastapi import status
import pytest

from app.telegram.handlers import MessageHandler, reply_unknown_user
from app.telegram.models import Bot, Chat


def gen_message(text):
    return {
        'update_id': 10000000,
        'message': {
            'message_id': 2434,
            'from': {
                'id': 666666,
                'is_bot': False,
                'first_name': 'Moshe',
                'username': 'banana',
                'language_code': 'en'
            },
            'chat': {
                'id': 666666,
                'first_name': 'Moshe',
                'username': 'banana',
                'type': 'private'
            },
            'date': 1611240725,
            'text': f'{text}'
        }
    }


def test_chat_model():
    chat = Chat(gen_message('Cool message'))
    assert chat.message == 'Cool message'
    assert chat.user_id == 666666
    assert chat.username == 'banana'
    assert chat.first_name == 'Moshe'


def test_bot_model():
    bot = Bot("fake bot id", "https://google.com")
    assert bot.base == 'https://api.telegram.org/botfake bot id/'
    assert bot.webhook_setter_url == 'https://api.telegram.org/botfake \
bot id/setWebhook?url=https://google.com/telegram/'

    assert bot.base == bot._set_base_url("fake bot id")
    assert bot.webhook_setter_url == bot._set_webhook_setter_url(
        "https://google.com")

    set_request = bot.set_webhook()
    assert set_request.status_code == 404
    assert set_request.json() == {
        'ok': False,
        'error_code': 404,
        'description': 'Not Found'
    }

    drop_request = bot.drop_webhook()
    assert drop_request.status_code == 404
    assert drop_request.json() == {
        'ok': False,
        'error_code': 404,
        'description': 'Not Found'
    }

    send_request = bot.send_message("654654645", "hello")
    assert send_request.status_code == 404
    assert send_request.json() == {
        'ok': False,
        'error_code': 404,
        'description': 'Not Found'
    }


def test_start_handlers():
    chat = Chat(gen_message('/start'))
    message = MessageHandler(chat)

    assert 'start' in message.handlers
    assert 'default' in message.handlers
    assert 'show_events' in message.handlers
    assert message.process_callback() == f'''Hello, {message.chat.first_name}!
Welcome to Pylander telegram client!'''


def test_default_handlers():
    wrong_start = MessageHandler(Chat(gen_message('start')))
    wrong_show_events = MessageHandler(Chat(gen_message('start')))
    message = MessageHandler(Chat(gen_message('hello')))

    assert wrong_start.process_callback() == "Unknown command"
    assert wrong_show_events.process_callback() == "Unknown command"
    assert message.process_callback() == "Unknown command"


def test_show_events_handler():
    chat = Chat(gen_message('/show_events'))
    message = MessageHandler(chat)
    assert message.process_callback() == 'Choose events day'


@pytest.mark.asyncio
async def test_reply_unknown_user():
    chat = Chat(gen_message('/show_events'))
    answer = await reply_unknown_user(chat)
    assert answer == '''
Hello, Moshe!

To use PyLander Bot you have to register
your Telegram Id in your profile page.

Your Id is 666666
Keep it secret!

https://calendar.pythonic.guru/profile/
'''


def test_telegram_router(profile_test_client):
    page = profile_test_client.get('/telegram')
    data = page.content
    assert page.ok is True
    assert b"Start using PyLander telegram bot!" in data


def test_bot_client(profile_test_client):

    page = profile_test_client.post(
        '/telegram', data=gen_message('/start'))
    assert page.status_code == status.HTTP_307_TEMPORARY_REDIRECT
