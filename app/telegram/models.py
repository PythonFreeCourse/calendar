from typing import Any, Dict, Optional

from httpx import AsyncClient


class Chat:
    def __init__(self, data: Dict):
        self.message = self._get_message_content(data)
        self.user_id = self._get_user_id(data)
        self.first_name = self._get_first_name(data)

    def _get_message_content(self, data: Dict) -> str:
        if 'callback_query' in data:
            return data['callback_query']['data']
        return data['message']['text']

    def _get_user_id(self, data: Dict) -> str:
        if 'callback_query' in data:
            return data['callback_query']['from']['id']
        return data['message']['from']['id']

    def _get_first_name(self, data: Dict) -> str:
        if 'callback_query' in data:
            return data['callback_query']['from']['first_name']
        return data['message']['from']['first_name']


class Bot:
    MEMORY = {}

    def __init__(self, bot_api: str, webhook_url: str):
        self.base = self._set_base_url(bot_api)
        self.webhook_setter_url = self._set_webhook_setter_url(webhook_url)

    def _set_base_url(self, bot_api: str) -> str:
        return f'https://api.telegram.org/bot{bot_api}/'

    def _set_webhook_setter_url(self, webhook_url: str) -> str:
        return f'{self.base}setWebhook?url={webhook_url}/telegram/'

    async def set_webhook(self):
        async with AsyncClient() as ac:
            return await ac.get(self.webhook_setter_url)

    async def drop_webhook(self):
        async with AsyncClient() as ac:
            data = {'drop_pending_updates': True}
            return await ac.post(url=f'{self.base}deleteWebhook', data=data)

    async def send_message(
            self, chat_id: str,
            text: str,
            reply_markup: Optional[Dict[str, Any]] = None):
        async with AsyncClient(base_url=self.base) as ac:
            message = {
                'chat_id': chat_id,
                'text': text}
            if reply_markup:
                message.update(reply_markup)
            return await ac.post('sendMessage', data=message)
