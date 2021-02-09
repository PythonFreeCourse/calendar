from fastapi.openapi.utils import get_openapi


def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    url = ('https://forums.pythonic.guru'
           '/uploads/default/original/1X/'
           '3c7e2ccc77e214fb4e38daa421f1b8878a5677f9.jpeg')
    openapi_schema = get_openapi(
        title="Pylander API",
        version="1.0.0",
        description="This is a custom OpenAPI schema for Pylander Developers",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        # TODO: change logo when we have one
        "url": url
    }
    app.openapi_schema = openapi_schema
    app.openapiv = app.openapi_schema
