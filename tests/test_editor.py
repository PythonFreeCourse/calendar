from app.internal.wysiwyg_editor import clean_html
import pytest

XXS_ATTACKS = [
    "<b onmouseover=alert('Wufff!')>click me!</b>",
    r"<img src=\"http://url.to.file.which/not.exist\" \
        onerror=alert(document.cookie);>",
    "<IMG SRC=j&#X41vascript:alert('test2')>",
    "<script>alert(‘XSS’)</script>",
    "http://testing.com/book.html?default= \
    <script>alert(document.cookie)</script>"]
# paramtrieze xss attacks


@pytest.mark.parametrize("text", XXS_ATTACKS)
def test_bleach_clean(text):
    cleaned = clean_html(text)
    assert cleaned != text
    # assert '&lt;' in cleaned or '&gt;' in cleaned


REGULAR_HTML = [
    "<p>hello</p>", "<h1>hello</h1>",
    "<div style=\"text-align: center;\"></div>",
    "<h1 class=\"title\">Your Title Text</h1>",
]


@pytest.mark.parametrize("text", REGULAR_HTML)
def test_dont_need_clean(text):
    cleaned = clean_html(text)
    print(cleaned)
    print(text)
    assert cleaned == text
    assert '&lt;' not in cleaned or '&gt;' not in cleaned
