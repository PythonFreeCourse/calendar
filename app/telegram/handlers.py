import datetime

import asyncio
import dateparser

from .keyboards import (
    DATE_FORMAT, field_kb, gen_inline_keyboard,
    get_this_week_buttons, new_event_kb, show_events_kb)
from .models import Chat
from .bot import telegram_bot
from app.database.database import get_db
from app.database.models import User
from app.routers.event import create_event


class MessageHandler:
    def __init__(self, chat: Chat, user: User):
        self.chat = chat
        self.user = user
        self.handlers = {}
        self.handlers['/start'] = self.start_handler
        self.handlers['/show_events'] = self.show_events_handler
        self.handlers['/new_event'] = self.new_event_handler
        self.handlers['Today'] = self.today_handler
        self.handlers['This week'] = self.this_week_handler

        # Add next 6 days to handlers dict
        for row in get_this_week_buttons():
            for button in row:
                self.handlers[button['text']] = self.chosen_day_handler

    async def process_callback(self):
        if self.chat.user_id in telegram_bot.MEMORY:
            return await self.process_new_event(
                telegram_bot.MEMORY[self.chat.user_id])
        elif self.chat.message in self.handlers:
            return await self.handlers[self.chat.message]()
        return await self.default_handler()

    async def default_handler(self):
        answer = "Unknown command."
        await telegram_bot.send_message(chat_id=self.chat.user_id, text=answer)
        return answer

    async def start_handler(self):
        answer = f'''Hello, {self.chat.first_name}!
Welcome to Pylander telegram client!'''
        await telegram_bot.send_message(chat_id=self.chat.user_id, text=answer)
        return answer

    async def show_events_handler(self):
        answer = 'Choose events day.'
        await telegram_bot.send_message(
            chat_id=self.chat.user_id,
            text=answer,
            reply_markup=show_events_kb)
        return answer

    async def today_handler(self):
        today = datetime.datetime.today()
        events = [
            _.events for _ in self.user.events
            if _.events.start <= today <= _.events.end]

        if not events:
            answer = "There're no events today."
            await telegram_bot.send_message(
                chat_id=self.chat.user_id, text=answer)
            return answer

        answer = f"{today.strftime('%A, %B %d')}:\n"
        await telegram_bot.send_message(
            chat_id=self.chat.user_id, text=answer)

        for event in events:
            start = event.start.strftime("%d %b %Y %H:%M")
            end = event.end.strftime("%d %b %Y %H:%M")
            answer = f'Title:\n{event.title}\n\n'
            answer += f'Content:\n{event.content}\n\n'
            answer += f'Location:\n{event.location}\n\n'
            answer += f'Starts on:\n{start}\n\n'
            answer += f'Ends on:\n{end}'
            await telegram_bot.send_message(
                chat_id=self.chat.user_id, text=answer)
            await asyncio.sleep(1)

        return answer

    async def this_week_handler(self):
        answer = 'Choose a day.'
        this_week_kb = gen_inline_keyboard(get_this_week_buttons())

        await telegram_bot.send_message(
            chat_id=self.chat.user_id,
            text=answer,
            reply_markup=this_week_kb)
        return answer

    async def chosen_day_handler(self):
        chosen_date = datetime.datetime.strptime(
            self.chat.message, DATE_FORMAT)

        events = [
            _.events for _ in self.user.events
            if _.events.start <= chosen_date <= _.events.end]

        if not events:
            answer = f"There're no events on {chosen_date.strftime('%B %d')}."
            await telegram_bot.send_message(
                chat_id=self.chat.user_id, text=answer)
            return answer

        answer = f"{chosen_date.strftime('%A, %B %d')}:\n"
        await telegram_bot.send_message(
            chat_id=self.chat.user_id, text=answer)

        for event in events:
            start = event.start.strftime("%d %b %Y %H:%M")
            end = event.end.strftime("%d %b %Y %H:%M")
            answer = f'Title:\n{event.title}\n\n'
            answer += f'Content:\n{event.content}\n\n'
            answer += f'Location:\n{event.location}\n\n'
            answer += f'Starts on:\n{start}\n\n'
            answer += f'Ends on:\n{end}'
            await telegram_bot.send_message(
                chat_id=self.chat.user_id, text=answer)
            await asyncio.sleep(1)

        return answer

    async def process_new_event(self, memo_dict):
        if self.chat.message == 'cancel':
            del telegram_bot.MEMORY[self.chat.user_id]
            answer = '🚫 The process was canceled.'
            await telegram_bot.send_message(
                chat_id=self.chat.user_id, text=answer)
            return answer

        elif self.chat.message == 'restart':
            answer = await self.new_event_handler()
            return answer

        elif 'title' not in memo_dict:
            memo_dict['title'] = self.chat.message
            answer = f'Title:\n{memo_dict["title"]}\n\n'
            answer += 'Add a description of the event.'
            await telegram_bot.send_message(
                chat_id=self.chat.user_id,
                text=answer,
                reply_markup=field_kb)
            return answer

        elif 'content' not in memo_dict:
            memo_dict['content'] = self.chat.message
            answer = f'Content:\n{memo_dict["content"]}\n\n'
            answer += 'Where the event will be held?'
            await telegram_bot.send_message(
                chat_id=self.chat.user_id,
                text=answer,
                reply_markup=field_kb)
            return answer

        elif 'location' not in memo_dict:
            memo_dict['location'] = self.chat.message
            answer = f'Location:\n{memo_dict["location"]}\n\n'
            answer += 'When does it start?'
            await telegram_bot.send_message(
                chat_id=self.chat.user_id,
                text=answer,
                reply_markup=field_kb)
            return answer

        elif 'start' not in memo_dict:
            date = dateparser.parse(self.chat.message)
            if date:
                memo_dict['start'] = date
                answer = f'Starts on:\n{date.strftime("%d %b %Y %H:%M")}\n\n'
                answer += 'And when does it end?'
                await telegram_bot.send_message(
                    chat_id=self.chat.user_id,
                    text=answer,
                    reply_markup=field_kb)
            else:
                answer = '❗️ Please, enter a valid date/time.'
                await telegram_bot.send_message(
                    chat_id=self.chat.user_id,
                    text=answer,
                    reply_markup=field_kb)
            return answer

        elif 'end' not in memo_dict:
            date = dateparser.parse(self.chat.message)
            if date:
                memo_dict['end'] = date
                start_time = memo_dict["start"].strftime("%d %b %Y %H:%M")
                answer = f'Title:\n{memo_dict["title"]}\n\n'
                answer += f'Content:\n{memo_dict["content"]}\n\n'
                answer += f'Location:\n{memo_dict["location"]}\n\n'
                answer += f'Starts on:\n{start_time}\n\n'
                answer += f'Ends on:\n{date.strftime("%d %b %Y %H:%M")}'
                await telegram_bot.send_message(
                    chat_id=self.chat.user_id,
                    text=answer,
                    reply_markup=new_event_kb)
            else:
                answer = '❗️ Please, enter a valid date/time.'
                await telegram_bot.send_message(
                    chat_id=self.chat.user_id, text=answer)
            return answer

        elif self.chat.message == 'create':
            answer = 'New event was successfully created 🎉'
            await telegram_bot.send_message(
                chat_id=self.chat.user_id, text=answer)

            # Save to database
            create_event(
                db=next(get_db()),
                title=memo_dict['title'],
                start=memo_dict['start'],
                end=memo_dict['end'],
                content=memo_dict['content'],
                owner_id=self.user.id,
                location=memo_dict['location'],
            )

            # Delete current session
            del telegram_bot.MEMORY[self.chat.user_id]

            return answer

    async def new_event_handler(self):
        telegram_bot.MEMORY[self.chat.user_id] = {}
        answer = 'Please, give your event a title.'
        await telegram_bot.send_message(
            chat_id=self.chat.user_id,
            text=answer,
            reply_markup=field_kb)
        return answer


async def reply_unknown_user(chat):
    answer = f'''
Hello, {chat.first_name}!

To use PyLander Bot you have to register
your Telegram Id in your profile page.

Your Id is {chat.user_id}
Keep it secret!

https://calendar.pythonic.guru/profile/
'''
    await telegram_bot.send_message(chat_id=chat.user_id, text=answer)
    return answer
