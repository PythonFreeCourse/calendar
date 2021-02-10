from app.routers import whatsapp
import pytest

def test_whatsapp_send():
    # Redirects you directly to the specified contact and the message will
    #  already be there (or to whatsapp web if the call is from the web)
    phone_number = "972536106106"
    message = 'Event or a joke or the schedule of one day'
    assert whatsapp.make_link(phone_number, message) == {
        "link": "https://api.whatsapp.com/send?phone=972536106106&text=Event+"
        "or+a+joke+or+the+schedule+of+one+day"}


def test_wrong_phone_number():
    # Redirects you to a popup: The phone number shared via a link is incorrect
    phone_number = "999999"
    message = 'Wrong phone number?'
    assert whatsapp.make_link(phone_number, message) == {
        "link": "https://api.whatsapp.com/send?phone=999999&text=Wrong+phone+"
        "number%3F"}


def test_no_message():
    # Redirects to whatsapp of the specified number. Write your own message.
    phone_number = "972536106106"
    message = ''
    assert whatsapp.make_link(phone_number, message) == {
        "link": "https://api.whatsapp.com/send?phone=972536106106&text="}


def test_no_number():
    # Redirects to whatsapp window. Choose someone from your own contact list.
    phone_number = ""
    message = 'Which phone number?'
    assert whatsapp.make_link(phone_number, message) == {
        "link": "https://api.whatsapp.com/send?phone=&text=Which+phone+"
        "number%3F"}


@pytest.mark.asyncio
async def test_end_to_end_testing(client):
    resp = await client.get('/whatsapp?phone_number=972536106106&message=testing')
    assert resp.ok
    assert resp.json
