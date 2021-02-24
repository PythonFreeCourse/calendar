from typing import Dict, Optional, Union
from datetime import datetime


def shabbat_time_by_user_location(
        shabbat_time: Dict[str, str]
) -> Dict[str, Union[str, datetime]]:
    """Returns the shabbat time of the user location..

        Args:
            Shabbat details.

        Returns:
            Shabbat start end ending time.
        """
    shabbat_limit = {
        'start_hour': shabbat_time['items'][5]['title'].split(': ')[1],
        'start_date': datetime.strptime(
            shabbat_time['items'][5]['date'].split('T')[0], "%Y-%m-%d"
        ).date(),
        'end_hour': shabbat_time['items'][7]['title'].split(': ')[1],
        'end_date': datetime.strptime(
            shabbat_time['items'][7]['date'].split('T')[0], "%Y-%m-%d"
        ).date()}
    return shabbat_limit


def get_shabbat_if_date_friday(
        shabbat_time: Dict[str, str],
        date: datetime
) -> Optional[Dict[str, Union[str, datetime]]]:
    """Returns shabbat start end ending time if specific date
     is Saturday, else None.

        Args:
            Shabbat details and date.

        Returns:
            Shabbat start end ending time if specific date
             is Saturday, else None
        """
    print(shabbat_time)
    shabbat_obj = shabbat_time_by_user_location(shabbat_time)
    if date == shabbat_obj['start_date']:
        return shabbat_obj
