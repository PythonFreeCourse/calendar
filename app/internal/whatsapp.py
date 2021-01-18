import webbrowser


def send(phone_number: str, message: str) -> bool:
    """This function is being used to send whatsapp messages.
    It takes a string message and a cell phone number and it sends the message to that phone number.
    Args:
        phone_number (str): Cell phone number to send the message to.
        message (str): Message that is going to be sent.

    Returns:
        bool: Returns True if the message was sent, else returns False.
    """
    try:
        webbrowser.open_new(f'https://api.whatsapp.com/send?phone={phone_number}&text={message}')
    except webbrowser.Error:  # pragma: no cover
        # Exception raised when a browser control error occurs.
        return False
    if not phone_number:
        return False
    if not message:
        return False
    return True