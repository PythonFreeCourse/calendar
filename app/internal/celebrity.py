import requests
from lxml import html
import datetime
from typing import Optional, Dict


BASE_URL = 'https://www.imdb.com/search/name/?birth_monthday='


def get_today_month_and_day() -> str:
    """Get today's month and day - %m-%d"""

    return datetime.date.today().strftime("%m-%d")


def get_content(today: str) -> Optional[bytes]:
    """Get IMDB HTML page content by today's birthdays"""

    url = BASE_URL + today

    try:
        page = requests.get(url)
    except requests.ConnectionError:
        # TODO: write error to log file
        return None
    else:
        if page.status_code == 200:
            return page.content
        return None


def get_celebs(today: str) -> Optional[Dict]:
    """Returns current day celebrity birthdays dictionary

    Args:
        today (str): current month-day formatted string (%m-%d)

    Returns:
        dict: A dictionary containing celebrities who celeberate
              their birthday's today.

    Information provided in dict:
        celebrity names, images, imdb profile links and jobs"""

    page = get_content(today)

    if page:
        tree = html.fromstring(page)
        names = tree.xpath('//h3[@class="lister-item-header"]/a/text()')[:12]
        names = (name[1:-1].strip() for name in names)
        images = tree.xpath(
            '//div[@class="lister-item-image"]/a/img/@src')[:12]
        links = tree.xpath('//div[@class="lister-item-image"]/a/@href')[:12]
        jobs = tree.xpath('//p[@class="text-muted text-small"]/text()')
        jobs = list(filter(None, [job.strip() for job in jobs]))[:12]

        return {key: dict(
            zip(['image', 'imdb_profile', 'job'],
            value)) for key, value in zip(names, zip(images, links, jobs))}

    return None