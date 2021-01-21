from typing import Optional


def make_link(phone_number: Optional[str], message: Optional[str]) -> str:
    """This function is being used to send whatsapp messages.
    It takes a string message and a cell phone number and it returns a link so we
    can add it to an html page and send the message to that phone number.
    Args:
        phone_number (str): Cell phone number to send the message to.
        message (str): Message that is going to be sent.

    Returns:
        str: Returns a string which contains a link to whatsapp api so we can
             send the message via whatsapp.
    """
    message = message.replace(" ", "%20")
    return f'https://api.whatsapp.com/send?phone={phone_number}&text={message}'
