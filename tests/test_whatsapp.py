from app.routers import whatsapp


def test_whatsapp_send():
    """Test with a valid phone number and text.

    Redirects directly to the specified contact and the message will
    already be there (or to WhatsApp Web if the call is from the web).

    """
    phone_number = "972536106106"
    message = 'Hello hello'
    expected = ("https://api.whatsapp.com/send?phone=972536106106&text="
                "Hello+hello")
    assert whatsapp.make_link(phone_number, message) == expected


def test_wrong_phone_number():
    """Text with invalid phone number and valid text.

    Redirects you to a popup: The phone number shared via a link is incorrect.

    """
    phone_number = "999999"
    message = 'Hello hello'
    expected = "https://api.whatsapp.com/send?phone=999999&text=Hello+hello"
    assert whatsapp.make_link(phone_number, message) == expected


def test_no_message():
    """Test with valid phone number and no text.

    Redirects to WhatsApp of the specified number. Write your own message.

    """
    phone_number = "972536106106"
    message = ''
    expected = "https://api.whatsapp.com/send?phone=972536106106&text="
    assert whatsapp.make_link(phone_number, message) == expected


def test_no_number():
    """Test with no phone number and valid text.

    Redirects to WhatsApp window. Choose someone from your own contact list.

    """
    phone_number = ""
    message = 'Hello hello'
    expected = "https://api.whatsapp.com/send?phone=&text=Hello+hello"
    assert whatsapp.make_link(phone_number, message) == expected


def test_end_to_end_testing(client):
    resp = client.get('/whatsapp?phone_number=972536106106&message=testing')
    assert resp.ok
    assert resp.json
