import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from app.dependencies import get_db
from app.database.models import (UserSettings, AudioTracks, User,
                                 UserAudioTracks)
from app.dependencies import SOUNDS_PATH, templates
from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm.session import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from enum import Enum


def get_placeholder_user():
    """Creates a placeholder user

    Returns:
        User: the new user.
    """
    return User(
        username='audio_user',
        email='audio@audio',
        password='audio525',
        full_name='audioaudio',
    )

DEFAULT_MUSIC = ["GASTRONOMICA.mp3"]
DEFAULT_MUSIC_VOL = 0.5
DEFAULT_SFX = "click_1.wav"
DEFAULT_SFX_VOL = 0.5


class SoundKind(Enum):
    SONG = 1
    SFX = 0


class Sound:
    def __init__(self, sound_kind, name, src):
        self.sound_kind = sound_kind
        self.name = name
        self.src = src


router = APIRouter(
    prefix="/audio",
    tags=["audio"],
    responses={404: {"description": "Not found"}},
)


@router.get("/settings")
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
    songs = [Sound(SoundKind.SONG, path.stem, path) for path in Path(SOUNDS_PATH).glob("**/*.mp3")]
    sound_effects = [Sound(SoundKind.SFX, path.stem, path) for path in Path(SOUNDS_PATH).glob("**/*.wav")]
    sounds = songs + sound_effects
    init_audio_tracks(session, sounds)

    return templates.TemplateResponse("audio_settings.html", {
        "request": request,
        'songs': songs,
        'sound_effects': sound_effects,
    })


@router.post("/settings")
async def get_choices(
    session: Session = Depends(get_db),
    new_user: User = Depends(get_placeholder_user),
    music_on: bool = Form(...),
    music_choices: Optional[List[str]] = Form(None),
    music_vol: Optional[int] = Form(None),
    sfx_on: bool = Form(...),
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
        {"music_on": music_on, "music_vol": music_vol,
         "sfx_on": sfx_on, "sfx_vol": sfx_vol})
    save_audio_settings(
        session, new_user, music_choices, sfx_choice, user_choices)

    return RedirectResponse("/", status_code=HTTP_302_FOUND)


@router.get("/start")
async def start_audio(session: Session = Depends(get_db),) -> RedirectResponse:
    """Starts audio according to audio settings.

    Args:
        session (Session): the database.

    Returns:
        RedirectResponse: redirect the user to home.html.
    """
    (music_on, playlist, music_vol,
        sfx_on, sfx_choice, sfx_vol) = get_audio_settings(session)
    if music_on is not None:
        music_vol = handle_vol(music_on, music_vol)
        sfx_vol = handle_vol(sfx_on, sfx_vol)

    if not playlist:
        playlist = DEFAULT_MUSIC
        music_vol = DEFAULT_MUSIC_VOL

    if not sfx_choice:
        chosen_sfx  = DEFAULT_SFX
        chosen_sfx_vol = DEFAULT_SFX_VOL
    else:
        chosen_sfx  = sfx_choice
        chosen_sfx_vol  = sfx_vol
    
    return json.dumps(
        {"music_on": music_on,
            "playlist": playlist,
            "music_vol": music_vol,
            "sfx_on": sfx_on,
            "sfx_choice": chosen_sfx,
            "sfx_vol": chosen_sfx_vol})


# Functions for audio setup according to users' choices:


def init_audio_tracks(
        session: Session,
        sounds : List[Sound]):
    """This function fills the AudioTracks table

    Args:
        session (Session): the database
        sounds (List[Sound]): list of sounds
    """
    for sound in sounds:
        add_sound(session, sound)


def add_sound(session: Session, sound: Sound):
    """Adds a new audio track to AudioTracks table.

    Args:
        session (Session): the databse.
        sound (Sound): song or sfx.
    """
    res = session.query(AudioTracks).filter_by(title=sound.name).first()
    if not res:
        track = AudioTracks(title=sound.name, is_music=sound.sound_kind.value)
        session.add(track)
        session.commit()


def get_tracks(
    session: Session,
    user_id: int
        ) -> Tuple[List[str], Optional[str]]:
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

    chosen_track_ids = session.query(
        UserAudioTracks.track_id).filter_by(user_id=user_id)

    tracks = session.query(
        AudioTracks).filter(
            AudioTracks.id.in_(chosen_track_ids)).filter_by(is_music=1)

    sfx = session.query(
        AudioTracks).filter(
            AudioTracks.id.in_(chosen_track_ids)).filter_by(is_music=0).first()

    for track in tracks:
        playlist.append(track.title + ".mp3")
    sfx_choice = sfx.title + ".wav" if sfx else None

    return playlist, sfx_choice


def get_audio_settings(
    session: Session, user_id: int = 1
) -> Tuple[Optional[List[str]], Optional[int], Optional[str], Optional[int]]:
    """Retrieves audio settings from the database.

    Args:
        session (Session): [description]
        user_id (int, optional): [description]. Defaults to 1.

    Returns:
        Tuple[str, Optional[List[str]], Optional[int],
        str, Optional[str], Optional[int]]: the audio settings.
    """
    music_on, music_vol, sfx_on, sfx_vol = None, None, None, None
    playlist, sfx_choice = get_tracks(session, user_id)
    audio_settings = session.query(
        UserSettings).filter_by(user_id=user_id).first()
    if audio_settings:
        music_on = audio_settings.music_on
        music_vol = audio_settings.music_vol
        sfx_on = audio_settings.sfx_on
        sfx_vol = audio_settings.sfx_vol

    return music_on, playlist, music_vol, sfx_on, sfx_choice, sfx_vol


def handle_vol(
    is_audio_on: bool,
    vol: Optional[int],
        ) -> Optional[int]:
    """Helper function that normalizes the volume and returns it,
    if audio is on.

    Args:
        is_audio_on (bool): True if the user chose to enable, False otherwise.
        vol (Optional[int]): a number in the range (0, 1),
        indicating the volume.
        example: 0.4 means 40% of the tracks' volume.

    Returns:
        Optional[int]: returns the normalized volume, or None if audio
        is disabled.
    """
    if is_audio_on:
        vol /= 100

    return vol


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
        including music_on, music_vol, sfx_on, sfx_vol
    """
    # need to change later to get the real user,
    # when registration feature is ready.
    user_name = "audio_user"
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
    """Insert or update a new record into UserSettings table.
    The table stores the following information:
    music on, music_vol, sfx on, sfx_vol.

    Args:
        session (Session): the database
        user (User): current user.
        user_choices (Dict[str, Union[str, int]]):
        including music_on, music_vol, sfx_on, sfx_vol
    """
    user_id = user.id
    audio_settings = session.query(UserSettings).filter_by(
        user_id=user_id).first()
    if not audio_settings:
        audio_settings = UserSettings(user_id=user_id, **user_choices)
        session.add(audio_settings)

    else:
        session.query(UserSettings).filter_by(
            user_id=audio_settings.user_id).update(user_choices)

    session.merge(audio_settings)


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
    choice = choice.split(".", maxsplit=1)[0]
    track = session.query(AudioTracks).filter_by(title=choice).first()
    track_id = track.id
    record = UserAudioTracks(user_id=user_id, track_id=track_id)
    session.add(record)
    session.commit()
