from fastapi import APIRouter, Body, Depends

from app.database.models import User
from app.dependencies import get_db
from app.telegram.handlers import MessageHandler, reply_unknown_user
from app.telegram.models import Chat

router = APIRouter(
    prefix="/telegram",
    tags=["telegram"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", include_in_schema=False)
async def bot_client(req: dict = Body(...), session=Depends(get_db)):
    chat = Chat(req)

    # Check if current chatter is registered to use the bot
    user = session.query(User).filter_by(telegram_id=chat.user_id).first()
    if user is None:
        return await reply_unknown_user(chat)

    message = MessageHandler(chat, user)
    return await message.process_callback()
