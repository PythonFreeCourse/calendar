from typing import Optional

from fastapi import APIRouter
from urllib.parse import urlencode

router = APIRouter(tags=["utils"])


@router.get("/whatsapp")
def make_link(phone_number: Optional[str], message: Optional[str]) -> str:
    """Returns a WhatsApp message URL.

    The message URL is built with the phone number and text message.

    Args:
        phone_number: Optional; The phone number to send the message to.
        message: Optional; The message sent.

    Returns:
        A WhatsApp message URL.
    """
    api = 'https://api.whatsapp.com/send?'
    url_query = {'phone': phone_number, 'text': message}
    link = api + urlencode(url_query)
    return link
