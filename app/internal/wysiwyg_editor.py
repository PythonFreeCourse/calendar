import bleach

# כתיבת טסטים
# טסטים לפי XXS


def clean_html(html: str) -> str:
    """
    This function is getting an html string and checking
    for malicious and not allowed tags, attrs and styles
    and then returns it cleaned without the not allowed parameters.

    Args:
        html (str): string from a post request made by the summernote editor.

    Returns:
        str: bleached string of html.
    """

    allowed_tags = [
        'a', 'abbr', 'b', 'blockquote', 'br', 'strike', 'u',
        'code', 'dd', 'del', 'div', 'dl', 'dt', 'em',
        'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li',
        'ol', 'p', 'pre', 's', 'strong', 'sub', 'sup',
        'table', 'tbody', 'td', 'th', 'thead', 'tr', 'ul', 'span', 'font'
    ]
    allowed_attrs = {
        '*': ['class', 'style'],
        'a': ['href', 'rel'],
        'abbr': ['title'],
        'style': ['font'],
        'font': ['color']
    }
    allowed_styles = [
        "text-align",
        'color', 'font-weight',
        'font color', 'background-color',
        'font', 'font-family', 'font-color'
    ]
    html_sanitized = bleach.clean(
        html,
        strip=True,
        tags=allowed_tags,
        attributes=allowed_attrs,
        styles=allowed_styles,
    )
    return html_sanitized
