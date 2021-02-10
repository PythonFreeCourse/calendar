import text2emotion as te
from typing import Dict, NamedTuple, Union

from app.config import (
    CONTENT_WEIGHTS,
    LEVEL_OF_SIGNIFICANCE,
    TITLE_WEIGHTS)


EMOTIONS = {"Happy": "&#128515",
            "Sad": "&#128577",
            "Angry": "&#128544",
            "Fear": "&#128561",
            "Surprise": "&#128558"}

Emoticon = NamedTuple("Emoticon", [("dominant", str), ("score", float),
                      ("code", str)])
DupEmotion = NamedTuple("DupEmotion", [("dominant", str), ("flag", bool)])


def get_weight(emotion: str, title_emotion: Dict[str, float],
               content_emotion: Dict[str, float] = None) -> float:
    if not content_emotion:
        return title_emotion[emotion]
    return (title_emotion[emotion] * TITLE_WEIGHTS +
            content_emotion[emotion] * CONTENT_WEIGHTS)


def score_comp(emotion_score: float, dominant_emotion: Emoticon, emotion: str,
               code: str, flag: bool) -> DupEmotion:
    """
    score comparison between emotions.
    returns the dominant and if equals we flag it
    """
    if emotion_score > dominant_emotion.score:
        flag = False
        dominant_emotion = Emoticon(dominant=emotion, score=emotion_score,
                                    code=code)
    elif emotion_score == dominant_emotion.score:
        flag = True
    return DupEmotion(dominant=dominant_emotion, flag=flag)


def get_dominant_emotion(title: str, content: str) -> Emoticon:
    """
    get text from event title and content and return
    the dominant emotion, emotion score and emoticon code
    """
    dominant_emotion = Emoticon(dominant=None, score=0, code=None)
    has_content = False
    duplicate_dominant_flag = False
    title_emotion = te.get_emotion(title)
    if content is not None and content.strip() != "":
        content_emotion = te.get_emotion(content)
        has_content = True
    for emotion, code in EMOTIONS.items():
        weight_parameters = [emotion, title_emotion]
        if has_content:
            weight_parameters.append(content_emotion)
        emotion_score = get_weight(*weight_parameters)
        score_comparison = score_comp(emotion_score, dominant_emotion, emotion,
                                      code, duplicate_dominant_flag)
        dominant_emotion, duplicate_dominant_flag = [*score_comparison]
    if duplicate_dominant_flag:
        return Emoticon(dominant=None, score=0, code=None)
    return dominant_emotion


def is_emotion_above_significance(dominant_emotion: Emoticon,
                                  significance: float =
                                  LEVEL_OF_SIGNIFICANCE) -> bool:
    """
    get the dominant emotion, emotion score and emoticon code
    and check if the emotion score above the constrain we set
    """
    return dominant_emotion.score >= significance


def get_html_emoticon(dominant_emotion: Emoticon) -> Union[str, None]:
    return dominant_emotion.code


def get_emotion(title: str, content: str) -> Union[str, None]:
    """
    The main function checks what the dominant emotion
    and if thr dominant emotion above the constrain we set
    return the emoticon code
    """
    dominant = get_dominant_emotion(title, content)
    if is_emotion_above_significance(dominant):
        return get_html_emoticon(dominant)
