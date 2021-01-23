from typing import Any, Dict, Optional

import requests


class Chat:
    def __init__(self, data):
        self.message = self._get_message_content(data)
        self.user_id = self._get_user_id(data)
        self.first_name = self._get_first_name(data)

    def _get_message_content(self, data):
        if 'callback_query' in data:
            return data['callback_query']['data']
        return data['message']['text']

    def _get_user_id(self, data):
        if 'callback_query' in data:
            return data['callback_query']['from']['id']
        return data['message']['from']['id']

    def _get_first_name(self, data):
        if 'callback_query' in data:
            return data['callback_query']['from']['first_name']
        return data['message']['from']['first_name']


class Bot:
    def __init__(self, bot_api: str, webhook_url: str):
        self.base = self._set_base_url(bot_api)
        self.webhook_setter_url = self._set_webhook_setter_url(webhook_url)

    def _set_base_url(self, bot_api):
        return f'https://api.telegram.org/bot{bot_api}/'

    def _set_webhook_setter_url(self, webhook_url: str):
        return f'{self.base}setWebhook?url={webhook_url}/telegram/'

    def set_webhook(self):
        return requests.get(self.webhook_setter_url)

    def drop_webhook(self):
        data = {
            'drop_pending_updates': True
        }
        return requests.get(
            url=f'{self.base}deleteWebhook', data=data)

    def send_message(
            self, chat_id: str,
            text: str,
            reply_markup: Optional[Dict[str, Any]] = None):
        message = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': None}
        if reply_markup:
            message.update(reply_markup)
        return requests.post(f'{self.base}sendMessage', data=message)
