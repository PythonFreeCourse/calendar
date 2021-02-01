import re

from fastapi import HTTPException

from starlette.status import HTTP_400_BAD_REQUEST

ZOOM_REGEX = re.compile(r'https://.*?\.zoom.us/[a-z]/.[^.,\b\s]+')


def validate_zoom_link(location):
    if ZOOM_REGEX.search(location) is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="VC type with no valid zoom link")
