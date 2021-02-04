from datetime import timedelta

from fastapi import status
import pytest

from .asyncio_fixture import today_date
from .client_fixture import get_test_placeholder_user
from app.telegram.handlers import MessageHandler, reply_unknown_user
# from app.telegram.keyboards import DATE_FORMAT
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


def gen_callback(text):
    return {
        'update_id': 568265,
        'callback_query': {
            'id': '546565356486',
            'from': {
                'id': 666666,
                'is_bot': False,
                'first_name': 'Moshe',
                'username': 'banana',
                'language_code': 'en'
            }, 'message': {
                'message_id': 838,
                'from': {
                    'id': 2566252,
                    'is_bot': True,
                    'first_name': 'PyLandar',
                    'username': 'pylander_bot'
                }, 'chat': {
                    'id': 666666,
                    'first_name': 'Moshe',
                    'username': 'banana',
                    'type': 'private'
                },
                'date': 161156,
                'text': 'Choose events day.',
                'reply_markup': {
                    'inline_keyboard': [
                        [
                            {
                                'text': 'Today',
                                'callback_data': 'Today'
                            },
                            {
                                'text': 'This week',
                                'callback_data': 'This week'
                            }
                        ]
                    ]
                }
            },
            'chat_instance': '-154494',
            'data': f'{text}'}}


class TestChatModel:

    @staticmethod
    def test_private_message():
        chat = Chat(gen_message('Cool message'))
        assert chat.message == 'Cool message'
        assert chat.user_id == 666666
        assert chat.first_name == 'Moshe'

    @staticmethod
    def test_callback_message():
        chat = Chat(gen_callback('Callback Message'))
        assert chat.message == 'Callback Message'
        assert chat.user_id == 666666
        assert chat.first_name == 'Moshe'


@pytest.mark.asyncio
async def test_bot_model():
    bot = Bot("fake bot id", "https://google.com")
    assert bot.base == 'https://api.telegram.org/botfake bot id/'
    assert bot.webhook_setter_url == 'https://api.telegram.org/botfake \
bot id/setWebhook?url=https://google.com/telegram/'

    assert bot.base == bot._set_base_url("fake bot id")
    assert bot.webhook_setter_url == bot._set_webhook_setter_url(
        "https://google.com")

    set_request = bot.set_webhook()
    assert set_request.status_code == status.HTTP_404_NOT_FOUND
    assert set_request.json() == {
        'ok': False,
        'error_code': 404,
        'description': 'Not Found'
    }

    drop_request = bot.drop_webhook()
    assert drop_request.status_code == status.HTTP_404_NOT_FOUND
    assert drop_request.json() == {
        'ok': False,
        'error_code': 404,
        'description': 'Not Found'
    }

    send_request = await bot.send_message("654654645", "hello")
    assert send_request.status_code == status.HTTP_404_NOT_FOUND
    assert send_request.json() == {
        'ok': False,
        'error_code': 404,
        'description': 'Not Found'
    }


class TestHandlers:
    TEST_USER = get_test_placeholder_user()

    @pytest.mark.asyncio
    async def test_start_handlers(self):
        chat = Chat(gen_message('/start'))
        message = MessageHandler(chat, self.TEST_USER)

        assert '/start' in message.handlers
        assert await message.process_callback() == '''Hello, Moshe!
Welcome to Pylander telegram client!'''

    @pytest.mark.asyncio
    async def test_default_handlers(self):
        wrong_start = MessageHandler(
            Chat(gen_message('start')), self.TEST_USER)
        wrong_show_events = MessageHandler(
            Chat(gen_message('show_events')), self.TEST_USER)
        message = MessageHandler(
            Chat(gen_message('hello')), self.TEST_USER)

        assert await wrong_start.process_callback() == "Unknown command."
        assert await wrong_show_events.process_callback() == "Unknown command."
        assert await message.process_callback() == "Unknown command."

    @pytest.mark.asyncio
    async def test_show_events_handler(self):
        chat = Chat(gen_message('/show_events'))
        message = MessageHandler(chat, self.TEST_USER)
        assert await message.process_callback() == 'Choose events day.'

    @pytest.mark.asyncio
    async def test_no_today_events_handler(self):
        chat = Chat(gen_callback('Today'))
        message = MessageHandler(chat, self.TEST_USER)
        assert await message.process_callback() == "There're no events today."

    @pytest.mark.asyncio
    async def test_today_handler(self, fake_user_events):
        chat = Chat(gen_callback('Today'))
        message = MessageHandler(chat, fake_user_events)
        assert await message.process_callback() == f'''\
{today_date.strftime('%B %d')}, {today_date.strftime('%A')} Events:

From {today_date.strftime('%d/%m %H:%M')} \
to {(today_date + timedelta(days=2)).strftime('%d/%m %H:%M')}: \
Cool today event.\n'''

    @pytest.mark.asyncio
    async def test_this_week_handler(self):
        chat = Chat(gen_callback('This week'))
        message = MessageHandler(chat, self.TEST_USER)
        assert await message.process_callback() == 'Choose a day.'

    @pytest.mark.asyncio
    async def test_no_chosen_day_handler(self):
        chat = Chat(gen_callback('10 Feb 2021'))
        message = MessageHandler(chat, self.TEST_USER)
        message.handlers['10 Feb 2021'] = message.chosen_day_handler
        assert await message.process_callback() == \
            "There're no events on February 10."

    """
     @pytest.mark.asyncio
        async def test_chosen_day_handler(self, fake_user_events):
            chosen_date = today_date + timedelta(days=2)
            button = str(chosen_date.strftime(DATE_FORMAT))
            chat = Chat(gen_callback(button))
            message = MessageHandler(chat, fake_user_events)
            message.handlers[button] = message.chosen_day_handler
            assert await message.chosen_day_handler() == f'''\
    {chosen_date.strftime('%B %d')}, {chosen_date.strftime('%A')} Events:
    From {today_date.strftime('%d/%m %H:%M')} \
    to {(today_date + timedelta(days=2)).strftime('%d/%m %H:%M')}: \
    Cool today event.
    From {(chosen_date + timedelta(days=-1)).strftime('%d/%m %H:%M')} \
    to {(chosen_date + timedelta(days=1)).strftime('%d/%m %H:%M')}: \
    Cool (somewhen in two days) event.\n'''
    """


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


class TestBotClient:
    """
    @staticmethod
        @pytest.mark.asyncio
        async def test_user_not_registered(telegram_client):
            response = await telegram_client.post(
                '/telegram/', json=gen_message('/start'))
            assert response.status_code == status.HTTP_200_OK
            assert b'Hello, Moshe!' in response.content
            assert b'To use PyLander Bot you have to register' \
                in response.content
    """

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_registered(telegram_client, session):
        session.add(get_test_placeholder_user())
        session.commit()
        response = await telegram_client.post(
            '/telegram/', json=gen_message('/start'))
        assert response.status_code == status.HTTP_200_OK
        assert b'Welcome to Pylander telegram client!' in response.content

    @staticmethod
    @pytest.mark.asyncio
    async def test_telegram_router(telegram_client):
        response = await telegram_client.get('/telegram')
        assert response.status_code == status.HTTP_200_OK
        assert b"Start using PyLander telegram bot!" in response.content
