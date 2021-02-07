from collections import namedtuple

import text2emotion as te
from typing import Union

from app.config import (
    CONTENT_WEIGHTS,
    LEVEL_OF_SIGNIFICANCE,
    TITLE_WEIGHTS)


EMOTIONS = {"Happy": "&#128515",
            "Sad": "&#128577",
            "Angry": "&#128544",
            "Fear": "&#128561",
            "Surprise": "&#128558"}

Emoticon = namedtuple("Emoticon",
                      ["dominant_emotion", "emotion_score", "emoticon_code"])


def dominant_emotion(title: str, content: str) -> Emoticon:
    """
    get text from event title and content and return
    the dominant emotion, emotion score and smiley code
    """
    DominantEmotion = Emoticon(None, 0, None)
    duplicate_dominant_flag = 0
    title_emotion = te.get_emotion(title)
    if content is not None:
        content_emotion = te.get_emotion(content)
    for emotion, code in EMOTIONS.items():
        if content not in (None, "", " "):
            emotion_score = (title_emotion[emotion] * TITLE_WEIGHTS +
                             content_emotion[emotion] * CONTENT_WEIGHTS)
        else:
            emotion_score = title_emotion[emotion]
        if emotion_score > DominantEmotion.emotion_score:
            DominantEmotion = Emoticon(emotion, emotion_score, code)
            duplicate_dominant_flag = 0
        elif emotion_score == DominantEmotion.emotion_score:
            duplicate_dominant_flag = 1
    if duplicate_dominant_flag:
        return Emoticon(None, 0, None)
    return DominantEmotion


def is_emotion_above_significance(DominantEmotion: Emoticon,
                                  significance: float =
                                  LEVEL_OF_SIGNIFICANCE) -> bool:
    """
    get the dominant emotion, emotion score and smiley code
    and check if the emotion score above the constrain we set
    """
    return DominantEmotion.emotion_score >= significance


def get_html_emoticon(DominantEmotion: Emoticon) -> Union[str, None]:
    return DominantEmotion.emoticon_code


def get_emotion(title: str, content: str) -> Union[str, None]:
    """
    The main function checks what the dominant emotion
    and if thr dominant emotion above the constrain we set
    return the smiley code
    """
    Dominant = dominant_emotion(title, content)
    if is_emotion_above_significance(Dominant):
        return get_html_emoticon(Dominant)
