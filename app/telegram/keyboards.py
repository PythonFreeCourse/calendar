import datetime
import json
from typing import Any, Dict, List


show_events_buttons = [
    [
        {'text': 'Today', 'callback_data': 'Today'},
        {'text': 'This week', 'callback_data': 'This week'}
    ]
]

DATE_FORMAT = '%d %b %Y'


def get_this_week_buttons() -> List[List[Any]]:
    today = datetime.date.today()
    day1 = today + datetime.timedelta(days=1)
    day2 = today + datetime.timedelta(days=2)
    day3 = today + datetime.timedelta(days=3)
    day4 = today + datetime.timedelta(days=4)
    day5 = today + datetime.timedelta(days=5)
    day6 = today + datetime.timedelta(days=6)

    return [
        [
            {'text': day1.strftime(DATE_FORMAT),
                'callback_data': day1.strftime(DATE_FORMAT)},
            {'text': day2.strftime(DATE_FORMAT),
                'callback_data': day2.strftime(DATE_FORMAT)},
            {'text': day3.strftime(DATE_FORMAT),
                'callback_data': day3.strftime(DATE_FORMAT)}
        ],
        [
            {'text': day4.strftime(DATE_FORMAT),
                'callback_data': day4.strftime(DATE_FORMAT)},
            {'text': day5.strftime(DATE_FORMAT),
                'callback_data': day5.strftime(DATE_FORMAT)},
            {'text': day6.strftime(DATE_FORMAT),
                'callback_data': day6.strftime(DATE_FORMAT)}
        ]
    ]


def gen_inline_keyboard(buttons: List[List[Any]]) -> Dict[str, Any]:
    return {'reply_markup': json.dumps({'inline_keyboard': buttons})}


show_events_kb = gen_inline_keyboard(show_events_buttons)
