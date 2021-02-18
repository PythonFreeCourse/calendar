import datetime


def get_today_month_and_day() -> str:
    """Returns today's month and day in the format: %m-%d"""
    return datetime.date.today().strftime("%m-%d")
