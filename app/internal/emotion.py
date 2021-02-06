import text2emotion as te
from typing import List, Union


# Emotion will appear if level of significance is equal or above this constrain
LEVEL_OF_SIGNIFICANCE = 0.45
# The weight of emotion based on event title
TITLE_WEIGHTS = 0.6
# The weight of emotion based on event content
CONTENT_WEIGHTS = 1 - TITLE_WEIGHTS


EMOTIONS = [("Happy", "&#128515"),
            ("Sad", "&#128577"),
            ("Angry", "&#128544"),
            ("Fear", "&#128561"),
            ("Surprise", "&#128558")]


def dominant_emotion(title: str, content: str) -> Union[List]:
    """
    get text from event title and content and return
    the dominant emotion, emotion score and smiley code
    """
    dominant_emotion = [None, 0, None]
    duplicate_dominant_flag = 0
    title_emotion = te.get_emotion(title)
    if content is not None:
        content_emotion = te.get_emotion(content)
    for emotion, code in EMOTIONS:
        if content not in (None, "", " "):
            emotion_score = (title_emotion[emotion] * TITLE_WEIGHTS +
                             content_emotion[emotion] * CONTENT_WEIGHTS)
        else:
            emotion_score = title_emotion[emotion]
        if emotion_score > dominant_emotion[1]:
            dominant_emotion = [emotion, emotion_score, code]
            duplicate_dominant_flag = 0
        elif emotion_score == dominant_emotion[1]:
            duplicate_dominant_flag = 1
    if duplicate_dominant_flag:
        return [None, 0, None]
    return dominant_emotion


def is_emotion_above_significance(dominant_emotion: Union[List],
                                  significance=LEVEL_OF_SIGNIFICANCE) -> bool:
    """
    get the dominant emotion, emotion score and smiley code
    and check if the emotion score above the constrain we set
    """
    return dominant_emotion[1] >= significance


def get_html_smiley(dominant_emotion: Union[List]) -> Union[str, None]:
    return dominant_emotion[2]


def get_emotion(title: str, content: str) -> Union[str, None]:
    """
    The main function checks what the dominant emotion
    and if thr dominant emotion above the constrain we set
    return the smiley code
    """
    dominant = dominant_emotion(title, content)
    if is_emotion_above_significance(dominant):
        return get_html_smiley(dominant)
