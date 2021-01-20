import pytest
from app.internal import whatslink


def test_whatsapp_send():
    # Works ok - The link will redirect you directly to the specified contact and the message will already be there (or to whatsapp web if the call is from the web)
    phone_number = "972536106106"
    message = 'Event or a joke or the schedule of one day'
    assert whatslink.make_link(phone_number, message) == f'https://api.whatsapp.com/send?phone=972536106106&text=Event%20or%20a%20joke%20or%20the%20schedule%20of%20one%20day'


def test_wrong_phone_number():
    # The link will redirect you to a popup: "The phone number shared via a link is incorrect"
    phone_number = "999999"
    message = 'Wrong phone number?'
    assert whatslink.make_link(phone_number, message) == f'https://api.whatsapp.com/send?phone=999999&text=Wrong%20phone%20number?'


def test_no_message():
    # The link will redirect to the whatsapp window of the specified number and you can write your own message
    phone_number = "972536106106"
    message = ''
    assert whatslink.make_link(phone_number, message) == f'https://api.whatsapp.com/send?phone=972536106106&text='


def test_no_number():
    # The link will redirect to whatsapp window and you can choose someone from your own contact list
    phone_number = ""
    message = 'Which phone number?'
    assert whatslink.make_link(phone_number, message) == f'https://api.whatsapp.com/send?phone=&text=Which%20phone%20number?'