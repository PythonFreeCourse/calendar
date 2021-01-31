import pytest
from app.internal.wysiwyg_editor import clean_html

XSS_ATTACKS = [
    "<b onmouseover=alert('Wufff!')>click me!</b>",
    r"<img src=\"http://url.to.file.which/not.exist\" \
        onerror=alert(document.cookie);>",
    "<IMG SRC=j&#X41vascript:alert('test2')>",
    "<script>alert(‘XSS’)</script>",
    "http://testing.com/book.html?default= \
    <script>alert(document.cookie)</script>"]


@pytest.mark.parametrize("text", XSS_ATTACKS)
def test_bleach_clean(text):
    cleaned = clean_html(text)
    assert cleaned != text
    assert "<script>" not in cleaned


REGULAR_HTML = [
    "<p>hello</p>", "<h1>hello</h1>",
    "<div style=\"text-align: center;\"></div>",
    "<h1 class=\"title\">Your Title Text</h1>",
]


@pytest.mark.parametrize("text", REGULAR_HTML)
def test_bleach_dont_need_clean(text):
    cleaned = clean_html(text)
    assert cleaned == text
    assert '&lt;' not in cleaned or '&gt;' not in cleaned
