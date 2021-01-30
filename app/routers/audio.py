import json
from pathlib import Path
from os import listdir
from typing import Dict, List, Optional, Tuple, Union

from app.database.database import get_db
from app.database.models import (AudioSettings, AudioTracks, User,
                                 UserAudioTracks)
from app.dependencies import SOUNDS_PATH, templates
from app.routers.profile import get_placeholder_user
from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm.session import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

DEFAULT_MUSIC = ["GASTRONOMICA.mp3"]
DEFAULT_MUSIC_VOL = 0.5
DEFAULT_SFX = "click 1.wav"
DEFAULT_SFX_VOL = 0.5
CHOSEN_SFX = Path(SOUNDS_PATH)
CHOSEN_SFX_VOL = None
AUDIO_SETTINGS_PATH = "/audio-settings"

router = APIRouter(
    prefix="/audio-settings",
    tags=["audio-settings"],
    responses={404: {"description": "Not found"}},
)

router2 = APIRouter(
    prefix="/start_audio",
    tags=["start_audio"],
    responses={404: {"description": "Not found"}},
)

router3 = APIRouter(
    prefix="/stop_audio",
    tags=["stop_audio"],
    responses={404: {"description": "Not found"}},
)

router4 = APIRouter(
    prefix="/free_achievement",
    tags=["free_achievement"],
    responses={404: {"description": "Not found"}},
)


# routes:


@router.get("/")
def audio_settings(
    request: Request, session: Session = Depends(get_db)
        ) -> templates.TemplateResponse:
    """A route to the audio settings.

    Args:
        request (Request): the http request
        session (Session): the database.

    Returns:
        templates.TemplateResponse: renders the audio.html page
        with the relevant information.
    """
    song_names = [Path(file).stem for file in listdir(
        SOUNDS_PATH) if Path(file).suffix == ".mp3"]
    sfx_names = [Path(file).stem for file in listdir(
        SOUNDS_PATH) if Path(file).suffix == ".wav"]
    init_audio_tracks(session, song_names, sfx_names)

    return templates.TemplateResponse("audio_settings.html", {
        "request": request,
        'song_names': song_names,
        'sfx_names': sfx_names,
    })


@router.post("/")
async def get_choices(
    session: Session = Depends(get_db),
    new_user: User = Depends(get_placeholder_user),
    music_on_off: str = Form(...),
    music_choices: Optional[List[str]] = Form(None),
    music_vol: Optional[int] = Form(None),
    sfx_on_off: str = Form(...),
    sfx_choice: Optional[str] = Form(None),
    sfx_vol: Optional[int] = Form(None)
        ) -> RedirectResponse:
    """This function saves users' choices in the db.

    Args:
        request (Request): the http request
        session (Session): the database.
        new_user (User): default user.
        need to be replaced with real one,
        after registration is implemented.
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

    Returns:
        RedirectResponse: redirect the user to home.html.
    """
    user_choices = (
        {"music_on": music_on_off, "music_vol": music_vol,
         "sfxs_on": sfx_on_off, "sfxs_vol": sfx_vol})
    save_audio_settings(
        session, new_user, music_choices, sfx_choice, user_choices)

    return RedirectResponse("/", status_code=HTTP_302_FOUND)


@router2.get("/")
async def start_audio(session: Session = Depends(get_db),) -> RedirectResponse:
    """Starts audio according to audio settings.

    Args:
        session (Session): the database.

    Returns:
        RedirectResponse: redirect the user to home.html.
    """
    (music_on, playlist, music_vol,
        sfxs_on, sfx_choice, sfxs_vol) = get_audio_settings(session)
    if music_on is not None:
        playlist, music_vol = handle_disabled_enabled(
            music_on, playlist, music_vol)
        sfx_choice, sfxs_vol = handle_disabled_enabled(
            sfxs_on, sfx_choice, sfxs_vol)

    if not playlist:
        playlist = DEFAULT_MUSIC
        music_vol = DEFAULT_MUSIC_VOL

    if not sfx_choice:
        CHOSEN_SFX = DEFAULT_SFX
        CHOSEN_SFX_VOL = DEFAULT_SFX_VOL
    else:
        CHOSEN_SFX = sfx_choice
        CHOSEN_SFX_VOL = sfxs_vol

    return json.dumps(
        {"music_on": music_on,
            "playlist": playlist,
            "music_vol": music_vol,
            "sfxs_on": sfxs_on,
            "sfx_choice": CHOSEN_SFX,
            "sfxs_vol": CHOSEN_SFX_VOL})


# Functions for audio setup according to users' choices:


def init_audio_tracks(
        session: Session,
        song_names: List[str],
        sfx_names: List[str]):
    """This function fills the AudioTracks table

    Args:
        session (Session): the database
        song_names (List[str]): list of song names
        sfx_names (List[str]): list of sfxs' names.
    """
    for song in song_names:
        add_audio_track(session, song, True)
    for sfx in sfx_names:
        add_audio_track(session, sfx, False)


def add_audio_track(session: Session, title: str, is_music: bool):
    """Adds a new audio track to AudioTracks table.

    Args:
        session (Session): the databse.
        title (str): title of the track.
        is_music (bool): if set to true - music, sfx otherwise.
    """
    res = session.query(AudioTracks).filter_by(title=title).first()
    if not res:
        track = AudioTracks(title=title, is_music=is_music)
        session.add(track)
        session.commit()


def get_tracks(
    session: Session,
    user_id: int
        ) -> Tuple[Optional[List[str]], Optional[str]]:
    """Retrieves audio selections from the database,
    for both music and sound effects.

    Args:
        session (Session): the database.
        user_id (int): current users' id.

    Returns:
        Tuple[Optional[List[str]], Optional[str]]:
        returns the playlist of music tracks, as well as sound effect choice.
    """
    playlist = []
    sfx_choice = None
    tracks = session.query(UserAudioTracks).filter_by(user_id=user_id)
    for track in tracks:
        track = session.query(AudioTracks).filter_by(id=track.track_id).first()
        if not track.is_music:
            sfx_choice = track.title + ".wav"
        else:
            playlist.append(track.title + ".mp3")

    return playlist, sfx_choice


def get_audio_settings(
    session: Session,
    user_id: int = 1
        ) -> (
            Tuple[Optional[List[str]],
                  Optional[int],
                  Optional[str],
                  Optional[int]]):
    """Retrieves audio settings from the database.

    Args:
        session (Session): [description]
        user_id (int, optional): [description]. Defaults to 1.

    Returns:
        Tuple[str, Optional[List[str]], Optional[int],
        str, Optional[str], Optional[int]]: the audio settings.
    """
    music_on, music_vol, sfxs_on, sfxs_vol = None, None, None, None
    playlist, sfx_choice = get_tracks(session, user_id)
    audio_settings = session.query(
        AudioSettings).filter_by(user_id=user_id).first()
    if audio_settings:
        music_on = audio_settings.music_on
        music_vol = audio_settings.music_vol
        sfxs_on = audio_settings.sfxs_on
        sfxs_vol = audio_settings.sfxs_vol

    return music_on, playlist, music_vol, sfxs_on, sfx_choice, sfxs_vol


def handle_disabled_enabled(
    audio_on_off: str,
    choices: Optional[List[str]],
    vol: Optional[int]
        ) -> Tuple[Optional[List[str]], Optional[int]]:
    """Helper function that sets irrelevant options
    to None in case the user chose to disable
    music/sfx. These options are the choices for the track and the volume.
    In case the user chose to enable music/sfx,
    we normalize the volume and return it, as well as the choices he made.

    Args:
        audio_on_off (str): On if the user chose to enable, Off otherwise.
        choices (Optional[List[str]]): A list of tracks or None if disabled.
        vol (Optional[int]): a number in the range (0, 1),
        indicating the volume.
        example: 0.4 means 40% of the tracks' volume.

    Returns:
        Tuple[Optional[List[str]], Optional[int]]: returns the chosen tracks,
        as well as the volume, or None if disabled.
    """
    if audio_on_off == "Off":
        choices = None
        vol = None
    else:
        vol /= 100
    return choices, vol


# Functions for saving users' choices in the db.


def save_audio_settings(
    session: Session,
    new_user: User,
    music_choices: Optional[List[str]],
    sfx_choice: Optional[str],
        user_choices: Dict[str, Union[str, int]]):
    """Save audio settings in the db.

    Args:
        session (Session): the database
        new_user (User): default user. need to be replaced with real
        one after registration is implemented
        music_choices (Optional[List[str]]): a list of music tracks
        f music is enabled, None otherwise.
        sfx_choice (Optional[str]): choice for sound effect.
        user_choices (Dict[str, Union[str, int]]):
        including music_on, music_vol, sfxs_on, sfxs_vol
    """
    # need to change later to get the real user,
    # when registration feature is ready.
    user_name = "new_user"
    user = get_user(session, user_name, new_user)
    user_id = user.id

    handle_audio_settings(session, user, user_choices)
    handle_user_audio_tracks(session, user_id, music_choices, sfx_choice)


def get_user(session: Session, user_name: str, new_user: User) -> User:
    """Retrieves user according to user_name.
    if he doesn't exist - returns default user (new_user).

    Args:
        session (Session): the database.
        user_name (str): name of the user.
        new_user (User): defualt user for the case that the
        user with user_name isn't found in the database.

    Returns:
        User: a user object.
    """
    user = session.query(User).filter_by(username=user_name).first()
    if not user:
        session.add(new_user)
        session.commit()
        user = session.query(User).filter_by(
            username=new_user.username).first()
    return user


def handle_audio_settings(
    session: Session,
    user: User,
        user_choices: Dict[str, Union[str, int]]):
    """Insert or update a new record into AudioSettings table.
    The table stores the following information:
    music on, music_vol, sfxs on, sfxs_vol.

    Args:
        session (Session): the database
        user (User): current user.
        user_choices (Dict[str, Union[str, int]]):
        including music_on, music_vol, sfxs_on, sfxs_vol
    """
    user_id = user.id
    audio_settings = session.query(AudioSettings).filter_by(
        user_id=user_id).first()
    if not audio_settings:
        audio_settings = AudioSettings(user_id=user_id, **user_choices)
        session.add(audio_settings)
        session.commit()

    else:
        session.query(AudioSettings).filter_by(
            user_id=audio_settings.user_id).update(user_choices)
        session.commit()


def handle_user_audio_tracks(
    session: Session,
    user_id: int,
    music_choices: Optional[List[str]],
        sfx_choice: Optional[str]):
    """[summary]

    Args:
        session (Session): the database.
        user_id (int): current users' id.
        music_choices (Optional[List[str]]):
        a list of music tracks if music is enabled, None otherwise.
        sfx_choice (Optional[str]): choice for sound effect.
    """
    user_audio_tracks = session.query(
        UserAudioTracks).filter_by(user_id=user_id)
    if user_audio_tracks:
        for record in user_audio_tracks:
            session.delete(record)
            session.commit()

    if music_choices:
        for track in music_choices:
            create_new_user_audio_record(session, track, user_id)
    if sfx_choice:
        create_new_user_audio_record(session, sfx_choice, user_id)


def create_new_user_audio_record(session: Session, choice, user_id: int):
    """Creates a new UserAudioTracks record.
    This is the table that connects users and audio_tracks tables.

    Args:
        session (Session): the database.
        choice ([type]): title of music track or sound effect.
        user_id (int): current users' id.
    """
    choice = choice.split(".")[0]
    track = session.query(AudioTracks).filter_by(title=choice).first()
    track_id = track.id
    record = UserAudioTracks(user_id=user_id, track_id=track_id)
    session.add(record)
    session.commit()
