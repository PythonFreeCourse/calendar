import json
from pathlib import Path
from typing import List, Optional

from app.database.models import User
from app.internal.audio import (
    get_audio_settings,
    handle_vol,
    SoundKind,
    Sound,
    init_audio_tracks,
    save_audio_settings,
    DEFAULT_MUSIC,
    DEFAULT_MUSIC_VOL,
    DEFAULT_SFX,
    DEFAULT_SFX_VOL,
)
from app.dependencies import SOUNDS_PATH, get_db, templates
from app.internal.security.dependancies import current_user
from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm.session import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND


router = APIRouter(
    prefix="/audio",
    tags=["audio"],
    responses={404: {"description": "Not found"}},
)


@router.get("/settings")
def audio_settings(
    request: Request,
    session: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> templates.TemplateResponse:
    """A route to the audio settings.

    Args:
        request (Request): the http request
        session (Session): the database.

    Returns:
        templates.TemplateResponse: renders the audio.html page
        with the relevant information.
    """
    mp3_files = Path(SOUNDS_PATH).glob("**/*.mp3")
    wav_files = Path(SOUNDS_PATH).glob("**/*.wav")
    songs = [Sound(SoundKind.SONG, path.stem, path) for path in mp3_files]
    sfxs = [Sound(SoundKind.SFX, path.stem, path) for path in wav_files]
    sounds = songs + sfxs
    init_audio_tracks(session, sounds)

    return templates.TemplateResponse(
        "audio_settings.html",
        {
            "request": request,
            "songs": songs,
            "sound_effects": sfxs,
        },
    )


@router.post("/settings")
async def get_choices(
    session: Session = Depends(get_db),
    music_on: bool = Form(...),
    music_choices: Optional[List[str]] = Form(None),
    music_vol: Optional[int] = Form(None),
    sfx_on: bool = Form(...),
    sfx_choice: Optional[str] = Form(None),
    sfx_vol: Optional[int] = Form(None),
    user: User = Depends(current_user),
) -> RedirectResponse:
    """This function saves users' choices in the db.

    Args:
        request (Request): the http request
        session (Session): the database.
        music_on_off (str, optional): On if the user chose to enable music,
        false otherwise.
        music_choices (Optional[List[str]], optional): a list of music tracks
        if music is enabled, None otherwise.
        music_vol (Optional[int], optional): a number in the range (0, 1)
        indicating the desired music volume, or None if disabled.
        sfx_on_off (str, optional): On if the user chose to enable
        sound effects, false otherwise.
        sfx_choice (Optional[str], optional): chosen sound effect for
        mouse click if sound effects are enabled, None otherwise.
        sfx_vol (Optional[int], optional): a number in the range (0, 1)
        indicating the desired sfx volume, or None if disabled.
        user (User): current user.

    Returns:
        RedirectResponse: redirect the user to home.html.
    """
    user_choices = {
        "music_on": music_on,
        "music_vol": music_vol,
        "sfx_on": sfx_on,
        "sfx_vol": sfx_vol,
    }
    save_audio_settings(session, music_choices, sfx_choice, user_choices, user)

    return RedirectResponse("/", status_code=HTTP_302_FOUND)


@router.get("/start")
async def start_audio(
    session: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> RedirectResponse:
    """Starts audio according to audio settings.

    Args:
        session (Session): the database.

    Returns:
        RedirectResponse: redirect the user to home.html.
    """
    (
        music_on,
        playlist,
        music_vol,
        sfx_on,
        sfx_choice,
        sfx_vol,
    ) = get_audio_settings(session, user.user_id)
    if music_on is not None:
        music_vol = handle_vol(music_on, music_vol)
        sfx_vol = handle_vol(sfx_on, sfx_vol)

    if not playlist:
        playlist = DEFAULT_MUSIC
        music_vol = DEFAULT_MUSIC_VOL

    if not sfx_choice:
        chosen_sfx = DEFAULT_SFX
        chosen_sfx_vol = DEFAULT_SFX_VOL
    else:
        chosen_sfx = sfx_choice
        chosen_sfx_vol = sfx_vol

    return json.dumps(
        {
            "music_on": music_on,
            "playlist": playlist,
            "music_vol": music_vol,
            "sfx_on": sfx_on,
            "sfx_choice": chosen_sfx,
            "sfx_vol": chosen_sfx_vol,
        },
    )
