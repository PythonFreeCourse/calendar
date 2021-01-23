import re

from fastapi import HTTPException

ZOOM_REGEX = re.compile(r'https://.*?\.zoom.us/[a-z]/.[^.,\b\t\n]+')


def validate_zoom_link(location):
    if not ZOOM_REGEX.findall(location):
        raise HTTPException(status_code=400,
                            detail="VC type with no valid zoom link")
