import requests


class Chat:
    def __init__(self, message):
        self.message = message['message']['text']
        self.user_id = message['message']['from']['id']
        self.username = message['message']['from']['username']
        self.first_name = message['message']['from']['first_name']


class Bot:
    def __init__(self, bot_api, webhook_url):
        self.base = self._set_base_url(bot_api)
        self.webhook_setter_url = self._set_webhook_setter_url(webhook_url)

    def _set_base_url(self, bot_api):
        return f'https://api.telegram.org/bot{bot_api}/'

    def _set_webhook_setter_url(self, webhook_url):
        return f'{self.base}setWebhook?url={webhook_url}/telegram/'

    def set_webhook(self):
        return requests.get(self.webhook_setter_url)

    def drop_webhook(self):
        url = f'{self.base}deleteWebhook'
        data = {
            'drop_pending_updates': True
        }
        return requests.get(url, data=data)

    def send_message(self, chat_id, text, reply_markup=[]):
        message = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': reply_markup
        }
        url = f'{self.base}sendMessage'
        return requests.post(url, data=message)
