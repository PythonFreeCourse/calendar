from .models import Chat
from .pylander import pylander


class MessageHandler:
    COMMANDS = ['/start', '/logout', '/show_events', '/new_event']

    def __init__(self, chat: Chat):
        self.chat = chat
        self.handlers = {}
        for method in dir(self):
            if method.endswith('_handler'):
                method_name = method[:-len('_handler')]
                self.handlers[method_name] = getattr(MessageHandler, method)

    def process_callback(self):
        if self.chat.message in self.COMMANDS:
            return self.handlers[self.chat.message[1:]](self)
        elif (self.chat.message in self.handlers
                and f'/{self.chat.message}' not in self.COMMANDS):
            return self.handlers[self.chat.message](self)
        else:
            return self.default_handler()

    def default_handler(self):
        answer = "Unknown command"
        pylander.send_message(chat_id=self.chat.user_id, text=answer)
        return answer

    def start_handler(self):
        answer = f'''Hello, {self.chat.first_name}!
Welcome to Pylander telegram client!'''
        pylander.send_message(chat_id=self.chat.user_id, text=answer)
        return answer

    def show_events_handler(self):
        answer = 'Choose events day'
        pylander.send_message(chat_id=self.chat.user_id, text=answer)
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
    pylander.send_message(chat_id=chat.user_id, text=answer)
    return answer
