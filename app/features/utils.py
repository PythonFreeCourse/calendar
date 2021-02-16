from functools import wraps
from starlette.responses import RedirectResponse

from app.internal.features import is_feature_enabled


def feature_access_filter(call_next):

    @wraps(call_next)
    async def wrapper(*args, **kwargs):
        request = kwargs['request']

        # getting the url route path for matching with the database.
        route = '/' + str(request.url).replace(str(request.base_url), '')

        # getting access status.
        is_enabled = is_feature_enabled(route=route)
        print(is_enabled)
        if is_enabled:
            # in case the feature is enabled or access is allowed.
            return await call_next(*args, **kwargs)

        elif 'referer' not in request.headers:
            # in case request come straight from address bar in browser.
            return RedirectResponse(url='/')

        # in case the feature is disabled or access isn't allowed.
        return RedirectResponse(url=request.headers['referer'])

    return wrapper
