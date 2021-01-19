
from fastapi import FastAPI
from app.internal.custom_logging import CustomizeLogger
from pathlib import Path
# from fastapi import Request
# import uvicorn
import logging
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates



# logger = logging.getLogger(__name__)

config_path=Path(__file__).parent / 'internal'
config_path = config_path.absolute() / "logging_config.json"


def create_app() -> FastAPI:
    app = FastAPI(title='Calendar', debug=False)
    logger = CustomizeLogger.make_logger(config_path)
    app.logger = logger

    return app


app = create_app()