from collections import namedtuple

import text2emotion as te
from typing import Dict, Tuple, Union

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


def get_weights(emotion: str, title_emotion: Dict[str, float],
                content_emotion: Dict[str, float] = None) -> float:
    if not content_emotion:
        return title_emotion[emotion]
    return (title_emotion[emotion] * TITLE_WEIGHTS +
            content_emotion[emotion] * CONTENT_WEIGHTS)


def score_comp(emotion_score: float, DominantEmotion: Emoticon, emotion: str,
               code: str, flag: int) -> Tuple[Emoticon, int]:
    """
    score comparison between emotions.
    returns the dominant and if equals we flag it
    """
    if emotion_score > DominantEmotion.emotion_score:
        flag = 0
        DominantEmotion = Emoticon(emotion, emotion_score, code)
    elif emotion_score == DominantEmotion.emotion_score:
        flag = 1
    return (DominantEmotion, flag)


def dominant_emotion(title: str, content: str) -> Emoticon:
    """
    get text from event title and content and return
    the dominant emotion, emotion score and emoticon code
    """
    DominantEmotion = Emoticon(None, 0, None)
    no_content = 1
    duplicate_dominant_flag = 0
    title_emotion = te.get_emotion(title)
    if content is not None and content.strip() != "":
        content_emotion = te.get_emotion(content)
        no_content = 0
    for emotion, code in EMOTIONS.items():
        if no_content:
            emotion_score = get_weights(emotion, title_emotion)
        else:
            emotion_score = get_weights(emotion, title_emotion,
                                        content_emotion)
        score_comparison = score_comp(emotion_score, DominantEmotion, emotion,
                                      code, duplicate_dominant_flag)
        DominantEmotion, duplicate_dominant_flag = [*score_comparison]
    if duplicate_dominant_flag:
        return Emoticon(None, 0, None)
    return DominantEmotion


def is_emotion_above_significance(DominantEmotion: Emoticon,
                                  significance: float =
                                  LEVEL_OF_SIGNIFICANCE) -> bool:
    """
    get the dominant emotion, emotion score and emoticon code
    and check if the emotion score above the constrain we set
    """
    return DominantEmotion.emotion_score >= significance


def get_html_emoticon(DominantEmotion: Emoticon) -> Union[str, None]:
    return DominantEmotion.emoticon_code


def get_emotion(title: str, content: str) -> Union[str, None]:
    """
    The main function checks what the dominant emotion
    and if thr dominant emotion above the constrain we set
    return the emoticon code
    """
    Dominant = dominant_emotion(title, content)
    if is_emotion_above_significance(Dominant):
        return get_html_emoticon(Dominant)
