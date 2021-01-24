import datetime

from .keyboards import (
    DATE_FORMAT, gen_inline_keyboard, get_this_week_buttons, show_events_kb)
from .models import Chat
from .pylander import pylander
from app.database.models import User


class MessageHandler:
    def __init__(self, chat: Chat, user: User):
        self.chat = chat
        self.user = user
        self.handlers = {}
        self.handlers['/start'] = self.start_handler
        self.handlers['/show_events'] = self.show_events_handler
        self.handlers['Today'] = self.today_handler
        self.handlers['This week'] = self.this_week_handler

        # Add next 6 days to handlers dict
        for row in get_this_week_buttons():
            for button in row:
                self.handlers[button['text']] = self.chosen_day_handler

    def process_callback(self):
        if self.chat.message in self.handlers:
            return self.handlers[self.chat.message]()
        return self.default_handler()

    def default_handler(self):
        answer = "Unknown command."
        pylander.send_message(chat_id=self.chat.user_id, text=answer)
        return answer

    def start_handler(self):
        answer = f'''Hello, {self.chat.first_name}!
Welcome to Pylander telegram client!'''
        pylander.send_message(chat_id=self.chat.user_id, text=answer)
        return answer

    def show_events_handler(self):
        answer = 'Choose events day.'
        pylander.send_message(
            chat_id=self.chat.user_id,
            text=answer,
            reply_markup=show_events_kb)
        return answer

    def today_handler(self):
        today = datetime.date.today()
        events = [
            event for event in self.user.events
            if event.start <= today <= event.end]

        answer = f"{today.strftime('%B %d')}, {today.strftime('%A')} Events:\n"

        if not len(events):
            answer = "There're no events today."

        for event in events:
            answer += f'\n\n{event.title}: from {event.start} to {event.ends}.'

        pylander.send_message(chat_id=self.chat.user_id, text=answer)
        return answer

    def this_week_handler(self):
        answer = 'Choose a day.'
        this_week_kb = gen_inline_keyboard(get_this_week_buttons())

        pylander.send_message(
            chat_id=self.chat.user_id,
            text=answer,
            reply_markup=this_week_kb)
        return answer

    def chosen_day_handler(self):
        # Convert chosen day (string) to datetime format
        chosen_date = datetime.datetime.strptime(
            self.chat.message, DATE_FORMAT)

        events = [
            event for event in self.user.events
            if event.start <= chosen_date <= event.end]

        answer = f"{chosen_date.strftime('%B %d')}, \
{chosen_date.strftime('%A')} Events:\n"

        if not len(events):
            answer = f"There're no events on {chosen_date.strftime('%B %d')}."

        for event in events:
            answer += f'\n\n{event.title}: from {event.start} to {event.ends}.'

        pylander.send_message(chat_id=self.chat.user_id, text=answer)
        return answer


def reply_unknown_user(chat):
    answer = f'''
Hello, {chat.first_name}!

To use PyLander Bot you have to register
your Telegram Id in your profile page.

Your Id is {chat.user_id}
Keep it secret!

https://calendar.pythonic.guru/profile/
'''
    pylander.send_message(chat_id=chat.user_id, text=answer)
    return answer
