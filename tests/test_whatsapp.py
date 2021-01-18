import pytest
from app.internal import whatsapp


phone_and_msg = [
    ('972536106106', 'Event or a joke or the schedule of one day'),
    # You will redirect to whatsapp window of the specified number and you can send the message
    ('999999', 'Wrong phone number?'),
    # You will redirect to whatsapp window and you will receive a message "The phone number shared via a link is incorrect"
]


@pytest.mark.parametrize('phone_number, message', phone_and_msg)
def test_whatsapp_send(phone_number, message):
    assert whatsapp.send(phone_number, message) == True


no_phone_or_msg = [
    ('972536106106', ''),
    # You will redirect to whatsapp window of the specified number and you can write your own message
    ('', 'Which phone number?'),
    # You will redirect to whatsapp window and you can choose someone from your contact list
]


@pytest.mark.parametrize('phone_number, message', no_phone_or_msg)
def test_no_message_or_phone(phone_number, message):
    assert whatsapp.send(phone_number, message) == False