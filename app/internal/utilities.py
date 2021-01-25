from typing import Any, Dict

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.dependencies import templates
from app.internal import languages


def get_template_response(html_file_name: str, request: Request,
                          variables: Dict[str, Any] = None) -> Jinja2Templates:
    """Creates and returns a Jinja2Templates object with a result dictionary
    containing three parts: the request object, a variables dictionary,
    and a translation dictionary.

    Args:
        html_file_name (str): the name of the html file.
        request (Request): a FastApi Request object.
        variables (Dict[str, Any]): an optional variables dictionary used
        in the html file.

    Returns:
        Jinja2Templates: a Jinja2Templates response object.
    """
    translations = languages.get_translation_words()
    result = {"request": request,
              "variables": variables,
              "localized": translations,
              }
    return templates.TemplateResponse(html_file_name, result)
