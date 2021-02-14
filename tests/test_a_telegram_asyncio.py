from datetime import datetime, timedelta

from fastapi import status
import pytest

from app.telegram.handlers import MessageHandler, reply_unknown_user
from app.telegram.keyboards import DATE_FORMAT
from app.telegram.models import Bot, Chat
from tests.asyncio_fixture import today_date
from tests.client_fixture import get_test_placeholder_user


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

    set_request = await bot.set_webhook()
    assert set_request.json() == {
        'ok': False,
        'error_code': 404,
        'description': 'Not Found'
    }

    drop_request = await bot.drop_webhook()
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


class TestBotClient:

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_not_registered(telegram_client):
        response = await telegram_client.post(
            '/telegram/', json=gen_message('/start'))
        assert response.status_code == status.HTTP_200_OK
        assert b'Hello, Moshe!' in response.content
        assert b'To use PyLendar Bot you have to register' \
               in response.content

    @staticmethod
    @pytest.mark.asyncio
    async def test_user_registered(telegram_client, session):
        session.add(get_test_placeholder_user())
        session.commit()
        response = await telegram_client.post(
            '/telegram/', json=gen_message('/start'))
        assert response.status_code == status.HTTP_200_OK
        assert b'Welcome to PyLendar telegram client!' in response.content


class TestHandlers:
    TEST_USER = get_test_placeholder_user()

    @pytest.mark.asyncio
    async def test_start_handlers(self):
        chat = Chat(gen_message('/start'))
        message = MessageHandler(chat, self.TEST_USER)

        assert '/start' in message.handlers
        assert await message.process_callback() == '''Hello, Moshe!
Welcome to PyLendar telegram client!'''

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
        answer = f"{today_date.strftime('%A, %B %d')}:\n"
        assert await message.process_callback() == answer

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
        answer = "There're no events on February 10."
        assert await message.process_callback() == answer

    @pytest.mark.asyncio
    async def test_chosen_day_handler(self, fake_user_events):
        chosen_date = today_date + timedelta(days=2)
        button = str(chosen_date.strftime(DATE_FORMAT))
        chat = Chat(gen_callback(button))
        message = MessageHandler(chat, fake_user_events)
        message.handlers[button] = message.chosen_day_handler
        answer = f"{chosen_date.strftime('%A, %B %d')}:\n"
        assert await message.chosen_day_handler() == answer

    @pytest.mark.asyncio
    async def test_new_event_handler(self):
        chat = Chat(gen_message('/new_event'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = 'Please, give your event a title.'
        assert await message.process_callback() == answer

    @pytest.mark.asyncio
    async def test_process_new_event(self):
        chat = Chat(gen_message('New Title'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = 'Title:\nNew Title\n\n'
        answer += 'Add a description of the event.'
        assert await message.process_callback() == answer

        chat = Chat(gen_message('New Content'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = 'Content:\nNew Content\n\n'
        answer += 'Where the event will be held?'
        assert await message.process_callback() == answer

        chat = Chat(gen_message('Universe'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = 'Location:\nUniverse\n\n'
        answer += 'When does it start?'
        assert await message.process_callback() == answer

        chat = Chat(gen_message('Not valid start datetime input'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = '❗️ Please, enter a valid date/time.'
        assert await message.process_callback() == answer

        chat = Chat(gen_message('today'))
        message = MessageHandler(chat, self.TEST_USER)
        today = datetime.today()
        answer = f'Starts on:\n{today.strftime("%d %b %Y %H:%M")}\n\n'
        answer += 'And when does it end?'
        assert await message.process_callback() == answer

        chat = Chat(gen_message('Not valid end datetime input'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = '❗️ Please, enter a valid date/time.'
        assert await message.process_callback() == answer

        chat = Chat(gen_message('tomorrow'))
        message = MessageHandler(chat, self.TEST_USER)
        tomorrow = today + timedelta(days=1)
        answer = 'Title:\nNew Title\n\n'
        answer += 'Content:\nNew Content\n\n'
        answer += 'Location:\nUniverse\n\n'
        answer += f'Starts on:\n{today.strftime("%d %b %Y %H:%M")}\n\n'
        answer += f'Ends on:\n{tomorrow.strftime("%d %b %Y %H:%M")}'
        assert await message.process_callback() == answer

        chat = Chat(gen_message('create'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = 'New event was successfully created 🎉'
        assert await message.process_callback() == answer

    @pytest.mark.asyncio
    async def test_process_new_event_cancel(self):
        chat = Chat(gen_message('/new_event'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = 'Please, give your event a title.'
        assert await message.process_callback() == answer

        chat = Chat(gen_message('cancel'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = '🚫 The process was canceled.'
        assert await message.process_callback() == answer

    @pytest.mark.asyncio
    async def test_process_new_event_restart(self):
        chat = Chat(gen_message('/new_event'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = 'Please, give your event a title.'
        assert await message.process_callback() == answer

        chat = Chat(gen_message('New Title'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = 'Title:\nNew Title\n\n'
        answer += 'Add a description of the event.'
        assert await message.process_callback() == answer

        chat = Chat(gen_message('restart'))
        message = MessageHandler(chat, self.TEST_USER)
        answer = 'Please, give your event a title.'
        assert await message.process_callback() == answer


@pytest.mark.asyncio
async def test_reply_unknown_user():
    chat = Chat(gen_message('/show_events'))
    answer = await reply_unknown_user(chat)
    assert answer == '''
Hello, Moshe!

To use PyLendar Bot you have to register
your Telegram Id in your profile page.

Your Id is 666666
Keep it secret!

https://calendar.pythonic.guru/profile/
'''
