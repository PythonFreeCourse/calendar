from typing import Any, Dict

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.dependencies import templates
from app.internal import languages


def get_template_response(html_file_name: str, request: Request,
                          variables: Dict[str, Any] = None) -> Jinja2Templates:
    translations = languages.get_translation_words()
    result = {"request": request,
              "variables": variables,
              "localized": translations,
              }
    return templates.TemplateResponse(html_file_name, result)
