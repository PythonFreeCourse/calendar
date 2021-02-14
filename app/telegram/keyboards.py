import datetime
import json
from typing import Any, Dict, List

show_events_buttons = [
    [
        {'text': 'Today', 'callback_data': 'Today'},
        {'text': 'This week', 'callback_data': 'This week'}
    ]
]

new_event_buttons = [
    [
        {'text': 'Create ✅', 'callback_data': 'create'},
        {'text': 'Cancel 🚫', 'callback_data': 'cancel'}
    ]
]

field_buttons = [
    [
        {'text': 'Restart 🚀', 'callback_data': 'restart'},
        {'text': 'Cancel 🚫', 'callback_data': 'cancel'}
    ]
]

DATE_FORMAT = '%d %b %Y'


def get_this_week_buttons() -> List[List[Any]]:
    today = datetime.datetime.today()
    buttons = []
    for day in range(1, 7):
        day = today + datetime.timedelta(days=day)
        buttons.append(day.strftime(DATE_FORMAT))

    return [
        [
            {
                'text': buttons[0],
                'callback_data': buttons[0],
            },
            {
                'text': buttons[1],
                'callback_data': buttons[1],
            },
            {
                'text': buttons[2],
                'callback_data': buttons[2],
            },
        ],
        [
            {
                'text': buttons[3],
                'callback_data': buttons[3],
            },
            {
                'text': buttons[4],
                'callback_data': buttons[4],
            },
            {
                'text': buttons[5],
                'callback_data': buttons[5],
            },
        ],
    ]


def gen_inline_keyboard(buttons: List[List[Any]]) -> Dict[str, Any]:
    return {'reply_markup': json.dumps({'inline_keyboard': buttons})}


show_events_kb = gen_inline_keyboard(show_events_buttons)
new_event_kb = gen_inline_keyboard(new_event_buttons)
field_kb = gen_inline_keyboard(field_buttons)
