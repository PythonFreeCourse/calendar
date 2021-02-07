import dateutil.parser
import requests

from datetime import datetime, timedelta

from typing import Any, Dict, List, Optional, Tuple


TOTAL_SEC_IN_HOUR = 3600
BLANK = ' '
UNDERSCORE = '_'
UNPACK_ELEMENT = 0
TIMEZONES_BASE_URL = 'http://worldtimeapi.org/api/timezone'
COUNTRY_TO_CONTINENT_DATA_SET = "https://pkgstore.datahub.io/JohnSnowLabs/" \
                                "country-and-continent-codes-list/" \
                                "country-and-continent-codes-list-csv_json/" \
                                "data/c218eebbf2f8545f3db9051ac893d69c/" \
                                "country-and-continent-codes-list-" \
                                "csv_json.json"
CITY_TO_COUNTRY_DATA_SET = "https://pkgstore.datahub.io/core/world-cities/" \
                           "world-cities_json/data/" \
                           "5b3dd46ad10990bca47b04b4739a02ba/" \
                           "world-cities_json.json"
TIMEZONES_COUNTRY_SUBCOUNTRY = {
    'Africa/Abidjan': {'country': 'Ivory Coast', 'subcountry': 'Lagunes'},
    'Africa/Accra': {'country': 'Ghana', 'subcountry': 'Greater Accra'},
    'Africa/Algiers': {'country': 'Algeria', 'subcountry': 'Alger'},
    'Africa/Bissau': {'country': 'Guinea-Bissau', 'subcountry': 'Bissau'},
    'Africa/Cairo': {'country': 'Egypt', 'subcountry': 'Cairo Governorate'},
    'Africa/Casablanca': {'country': 'Morocco',
                          'subcountry': 'Grand Casablanca'},
    'Africa/Ceuta': {'country': 'Spain', 'subcountry': 'Ceuta'},
    'Africa/Johannesburg': {'country': 'South Africa',
                            'subcountry': 'Gauteng'},
    'Africa/Juba': {'country': 'Jordan', 'subcountry': 'Amman'},
    'Africa/Khartoum': {'country': 'Sudan', 'subcountry': 'Khartoum'},
    'Africa/Lagos': {'country': 'Mexico', 'subcountry': 'Jalisco'},
    'Africa/Maputo': {'country': 'Mozambique',
                      'subcountry': 'Maputo City'},
    'Africa/Monrovia': {'country': 'Liberia',
                        'subcountry': 'Montserrado'},
    'Africa/Nairobi': {'country': 'Kenya', 'subcountry': 'Nairobi Area'},
    'Africa/Tripoli': {'country': 'Lebanon', 'subcountry': 'Liban-Nord'},
    'Africa/Tunis': {'country': 'Tunisia', 'subcountry': 'Tunis'},
    'Africa/Windhoek': {'country': 'Namibia', 'subcountry': 'Khomas'},
    'America/Anchorage': {'country': 'United States',
                          'subcountry': 'Alaska'},
    'America/Argentina/Buenos_Aires': {'country': 'Argentina',
                                       'subcountry': 'Buenos Aires F.D.'},
    'America/Argentina/Catamarca': {'country': 'Argentina',
                                    'subcountry': 'Catamarca'},
    'America/Argentina/Jujuy': {'country': 'Argentina',
                                'subcountry': 'Jujuy'},
    'America/Argentina/La_Rioja': {'country': 'Argentina',
                                   'subcountry': 'La Rioja'},
    'America/Argentina/Mendoza': {'country': 'Argentina',
                                  'subcountry': 'Mendoza'},
    'America/Argentina/Salta': {'country': 'Argentina',
                                'subcountry': 'Salta'},
    'America/Argentina/San_Juan': {'country': 'Argentina',
                                   'subcountry': 'San Juan'},
    'America/Argentina/San_Luis': {'country': 'Argentina',
                                   'subcountry': 'Corrientes'},
    'America/Argentina/Ushuaia': {'country': 'Argentina',
                                  'subcountry': 'Tierra del Fuego'},
    'America/Belize': {'country': 'Belize', 'subcountry': 'Belize'},
    'America/Boa_Vista': {'country': 'Brazil', 'subcountry': 'Sao Paulo'},
    'America/Boise': {'country': 'United States', 'subcountry': 'Idaho'},
    'America/Campo_Grande': {'country': 'Brazil',
                             'subcountry': 'Mato Grosso do Sul'},
    'America/Caracas': {'country': 'Venezuela', 'subcountry': 'Capital'},
    'America/Cayenne': {'country': 'French Guiana', 'subcountry': 'Guyane'},
    'America/Chicago': {'country': 'United States',
                        'subcountry': 'Illinois'},
    'America/Chihuahua': {'country': 'Mexico', 'subcountry': 'Chihuahua'},
    'America/Costa_Rica': {'country': 'Mexico', 'subcountry': 'Sinaloa'},
    'America/Denver': {'country': 'United States',
                       'subcountry': 'Colorado'},
    'America/Detroit': {'country': 'United States',
                        'subcountry': 'Michigan'},
    'America/Edmonton': {'country': 'Canada', 'subcountry': 'Alberta'},
    'America/Fortaleza': {'country': 'Brazil', 'subcountry': 'Ceará'},
    'America/Glace_Bay': {'country': 'Canada', 'subcountry': 'Nova Scotia'},
    'America/Guatemala': {'country': 'Guatemala',
                          'subcountry': 'Chimaltenango'},
    'America/Guayaquil': {'country': 'Ecuador', 'subcountry': 'Guayas'},
    'America/Halifax': {'country': 'Canada', 'subcountry': 'Nova Scotia'},
    'America/Havana': {'country': 'Cuba', 'subcountry': 'La Habana'},
    'America/Hermosillo': {'country': 'Mexico', 'subcountry': 'Sonora'},
    'America/Indiana/Indianapolis': {'country': 'United States',
                                     'subcountry': 'Indiana'},
    'America/Indiana/Knox': {'country': 'United States',
                             'subcountry': 'Tennessee'},
    'America/Indiana/Petersburg': {'country': 'Russia',
                                   'subcountry': 'St.-Petersburg'},
    'America/Indiana/Vincennes': {'country': 'France',
                                  'subcountry': 'Ile-de-France'},
    'America/Jamaica': {'country': 'United States',
                        'subcountry': 'Massachusetts'},
    'America/Juneau': {'country': 'United States', 'subcountry': 'Alaska'},
    'America/Kentucky/Louisville': {'country': 'United States',
                                    'subcountry': 'Kentucky'},
    'America/La_Paz': {'country': 'Argentina', 'subcountry': 'Entre Rios'},
    'America/Lima': {'country': 'Brazil', 'subcountry': 'Pernambuco'},
    'America/Los_Angeles': {'country': 'United States',
                            'subcountry': 'California'},
    'America/Managua': {'country': 'Nicaragua', 'subcountry': 'Managua'},
    'America/Manaus': {'country': 'Brazil', 'subcountry': 'Amazonas'},
    'America/Matamoros': {'country': 'Mexico', 'subcountry': 'Tamaulipas'},
    'America/Mexico_City': {'country': 'Mexico',
                            'subcountry': 'Mexico City'},
    'America/Moncton': {'country': 'Canada',
                        'subcountry': 'New Brunswick'},
    'America/Monterrey': {'country': 'Mexico', 'subcountry': 'Nuevo León'},
    'America/Montevideo': {'country': 'Uruguay',
                           'subcountry': 'Montevideo'},
    'America/Nassau': {'country': 'Bahamas',
                       'subcountry': 'New Providence'},
    'America/New_York': {'country': 'United States',
                         'subcountry': 'New Jersey'},
    'America/North_Dakota/Center': {'country': 'United States',
                                    'subcountry': 'North Dakota'},
    'America/Nuuk': {'country': 'Greenland', 'subcountry': 'Sermersooq'},
    'America/Ojinaga': {'country': 'Mexico', 'subcountry': 'Chihuahua'},
    'America/Panama': {'country': 'United States', 'subcountry': 'Florida'},
    'America/Paramaribo': {'country': 'Suriname',
                           'subcountry': 'Paramaribo'},
    'America/Phoenix': {'country': 'United States',
                        'subcountry': 'Pennsylvania'},
    'America/Port-au-Prince': {'country': 'Haiti', 'subcountry': 'Ouest'},
    'America/Port_of_Spain': {'country': 'Trinidad and Tobago',
                              'subcountry': 'City of Port of Spain'},
    'America/Porto_Velho': {'country': 'Brazil',
                            'subcountry': 'Rond?nia'},
    'America/Puerto_Rico': {'country': 'Argentina',
                            'subcountry': 'Misiones'},
    'America/Punta_Arenas': {'country': 'Chile',
                             'subcountry': 'Magallanes'},
    'America/Recife': {'country': 'Brazil', 'subcountry': 'Pernambuco'},
    'America/Regina': {'country': 'Argentina',
                       'subcountry': 'Rio Negro'},
    'America/Rio_Branco': {'country': 'Brazil',
                           'subcountry': 'Minas Gerais'},
    'America/Santiago': {'country': 'Argentina',
                         'subcountry': 'Santiago del Estero'},
    'America/Santo_Domingo': {'country': 'Cuba',
                              'subcountry': 'Villa Clara'},
    'America/Tegucigalpa': {'country': 'Honduras',
                            'subcountry': 'Francisco Morazán'},
    'America/Thunder_Bay': {'country': 'Canada', 'subcountry': 'Ontario'},
    'America/Tijuana': {'country': 'Mexico',
                        'subcountry': 'Baja California'},
    'America/Toronto': {'country': 'Canada',
                        'subcountry': 'Ontario'},
    'America/Vancouver': {'country': 'Canada',
                          'subcountry': 'British Columbia'},
    'America/Whitehorse': {'country': 'Canada',
                           'subcountry': 'Yukon'},
    'America/Winnipeg': {'country': 'Canada',
                         'subcountry': 'Manitoba'},
    'America/Yellowknife': {'country': 'Canada',
                            'subcountry': 'Northwest Territories'},
    'Antarctica/Davis': {'country': 'United States',
                         'subcountry': 'California'},
    'Antarctica/Macquarie': {'country': 'Australia',
                             'subcountry': 'New South Wales'},
    'Antarctica/Palmer': {'country': 'Australia',
                          'subcountry': 'Northern Territory'},
    'Antarctica/Troll': {'country': 'Sweden',
                         'subcountry': 'V?stra G?taland'},
    'Asia/Almaty': {'country': 'Kazakhstan',
                    'subcountry': 'Almaty Qalasy'},
    'Asia/Amman': {'country': 'Jordan', 'subcountry': 'Amman'},
    'Asia/Ashgabat': {'country': 'Turkmenistan', 'subcountry': 'Ahal'},
    'Asia/Atyrau': {'country': 'Kazakhstan', 'subcountry': 'Atyrau'},
    'Asia/Baghdad': {'country': 'Iraq',
                     'subcountry': 'Mayorality of Baghdad'},
    'Asia/Baku': {'country': 'Azerbaijan', 'subcountry': 'Baki'},
    'Asia/Bangkok': {'country': 'Thailand', 'subcountry': 'Bangkok'},
    'Asia/Barnaul': {'country': 'Russia', 'subcountry': 'Altai Krai'},
    'Asia/Beirut': {'country': 'Lebanon', 'subcountry': 'Beyrouth'},
    'Asia/Bishkek': {'country': 'Kyrgyzstan', 'subcountry': 'Bishkek'},
    'Asia/Chita': {'country': 'Russia',
                   'subcountry': 'Transbaikal Territory'},
    'Asia/Colombo': {'country': 'Brazil', 'subcountry': 'Paraná'},
    'Asia/Damascus': {'country': 'Syria', 'subcountry': 'Dimashq'},
    'Asia/Dhaka': {'country': 'Bangladesh', 'subcountry': 'Dhaka'},
    'Asia/Dili': {'country': 'Egypt', 'subcountry': 'Al Bu?ayrah'},
    'Asia/Dubai': {'country': 'United Arab Emirates',
                   'subcountry': 'Dubai'},
    'Asia/Dushanbe': {'country': 'Tajikistan',
                      'subcountry': 'Dushanbe'},
    'Asia/Famagusta': {'country': 'Cyprus',
                       'subcountry': 'Ammochostos'},
    'Asia/Gaza': {'country': 'Palestinian Territory',
                  'subcountry': 'Gaza Strip'},
    'Asia/Hebron': {'country': 'Palestinian Territory',
                    'subcountry': 'West Bank'},
    'Asia/Ho_Chi_Minh': {'country': 'Vietnam',
                         'subcountry': 'Ho Chi Minh City'},
    'Asia/Hong_Kong': {'country': 'Hong Kong',
                       'subcountry': 'Central and Western'},
    'Asia/Hovd': {'country': 'Mongolia', 'subcountry': '?v?rhangay'},
    'Asia/Irkutsk': {'country': 'Russia', 'subcountry': 'Irkutsk'},
    'Asia/Jakarta': {'country': 'Indonesia',
                     'subcountry': 'Jakarta Raya'},
    'Asia/Jayapura': {'country': 'Indonesia', 'subcountry': 'Papua'},
    'Asia/Jerusalem': {'country': 'Israel',
                       'subcountry': 'Jerusalem'},
    'Asia/Kabul': {'country': 'Afghanistan', 'subcountry': 'Kabul'},
    'Asia/Karachi': {'country': 'Pakistan', 'subcountry': 'Sindh'},
    'Asia/Kathmandu': {'country': 'Nepal',
                       'subcountry': 'Central Region'},
    'Asia/Kolkata': {'country': 'India', 'subcountry': 'West Bengal'},
    'Asia/Krasnoyarsk': {'country': 'Russia',
                         'subcountry': 'Krasnoyarskiy'},
    'Asia/Kuala_Lumpur': {'country': 'Malaysia',
                          'subcountry': 'Kuala Lumpur'},
    'Asia/Kuching': {'country': 'Malaysia', 'subcountry': 'Sarawak'},
    'Asia/Macau': {'country': 'Brazil',
                   'subcountry': 'Rio Grande do Norte'},
    'Asia/Magadan': {'country': 'Russia', 'subcountry': 'Magadan'},
    'Asia/Makassar': {'country': 'Indonesia',
                      'subcountry': 'South Sulawesi'},
    'Asia/Manila': {'country': 'Philippines',
                    'subcountry': 'Metro Manila'},
    'Asia/Nicosia': {'country': 'Cyprus', 'subcountry': 'Lefkosia'},
    'Asia/Novokuznetsk': {'country': 'Russia',
                          'subcountry': 'Kemerovo'},
    'Asia/Novosibirsk': {'country': 'Russia',
                         'subcountry': 'Novosibirsk'},
    'Asia/Omsk': {'country': 'Russia', 'subcountry': 'Omsk'},
    'Asia/Oral': {'country': 'Kazakhstan',
                  'subcountry': 'Batys Qazaqstan'},

    'Asia/Pontianak': {'country': 'Indonesia',
                       'subcountry': 'West Kalimantan'},
    'Asia/Pyongyang': {'country': 'North Korea',
                       'subcountry': 'Pyongyang'},
    'Asia/Riyadh': {'country': 'Saudi Arabia',
                    'subcountry': 'Ar Riya?'},
    'Asia/Sakhalin': {'country': 'Russia',
                      'subcountry': 'Sakhalin'},
    'Asia/Seoul': {'country': 'South Korea',
                   'subcountry': 'Seoul'},
    'Asia/Shanghai': {'country': 'China',
                      'subcountry': 'Shanghai Shi'},
    'Asia/Singapore': {'country': 'Singapore',
                       'subcountry': 'Central Singapore'},
    'Asia/Taipei': {'country': 'Taiwan', 'subcountry': 'Taipei'},
    'Asia/Tashkent': {'country': 'Uzbekistan',
                      'subcountry': 'Toshkent Shahri'},
    'Asia/Tbilisi': {'country': 'Georgia',
                     'subcountry': "T'bilisi"},
    'Asia/Tehran': {'country': 'Iran', 'subcountry': 'Tehran'},
    'Asia/Thimphu': {'country': 'Bhutan',
                     'subcountry': 'Thimphu'},
    'Asia/Tokyo': {'country': 'Japan', 'subcountry': 'Tokyo'},
    'Asia/Tomsk': {'country': 'Russia', 'subcountry': 'Tomsk'},
    'Asia/Vladivostok': {'country': 'Russia',
                         'subcountry': 'Primorskiy'},
    'Asia/Yakutsk': {'country': 'Russia', 'subcountry': 'Sakha'},
    'Asia/Yangon': {'country': 'Myanmar', 'subcountry': 'Yangon'},
    'Asia/Yekaterinburg': {'country': 'Russia',
                           'subcountry': 'Sverdlovsk'},
    'Asia/Yerevan': {'country': 'Armenia', 'subcountry': 'Yerevan'},
    'Atlantic/Canary': {'country': 'United Kingdom',
                        'subcountry': 'England'},
    'Atlantic/Madeira': {'country': 'Portugal', 'subcountry': 'Aveiro'},
    'Atlantic/Stanley': {'country': 'Falkland Islands',
                         'subcountry': 'N/A'},
    'Australia/Adelaide': {'country': 'Australia',
                           'subcountry': 'South Australia'},
    'Australia/Brisbane': {'country': 'Australia',
                           'subcountry': 'Queensland'},
    'Australia/Broken_Hill': {'country': 'Australia',
                              'subcountry': 'New South Wales'},
    'Australia/Darwin': {'country': 'Australia',
                         'subcountry': 'Northern Territory'},
    'Australia/Hobart': {'country': 'Australia', 'subcountry': 'Tasmania'},
    'Australia/Melbourne': {'country': 'Australia',
                            'subcountry': 'Victoria'},
    'Australia/Perth': {'country': 'Australia',
                        'subcountry': 'Western Australia'},
    'Australia/Sydney': {'country': 'Australia',
                         'subcountry': 'New South Wales'},
    'Europe/Amsterdam': {'country': 'Guyana',
                         'subcountry': 'East Berbice-Corentyne'},
    'Europe/Andorra': {'country': 'Andorra',
                       'subcountry': 'Andorra la Vella'},
    'Europe/Astrakhan': {'country': 'Russia',
                         'subcountry': 'Astrakhan'},
    'Europe/Athens': {'country': 'Greece', 'subcountry': 'Attica'},
    'Europe/Belgrade': {'country': 'Serbia',
                        'subcountry': 'Central Serbia'},
    'Europe/Berlin': {'country': 'Germany', 'subcountry': 'Berlin'},
    'Europe/Brussels': {'country': 'Belgium',
                        'subcountry': 'Brussels Capital'},
    'Europe/Bucharest': {'country': 'Romania',
                         'subcountry': 'Bucuresti'},
    'Europe/Budapest': {'country': 'Hungary',
                        'subcountry': 'Budapest'},
    'Europe/Copenhagen': {'country': 'Denmark',
                          'subcountry': 'Capital Region'},
    'Europe/Dublin': {'country': 'Ireland', 'subcountry': 'Leinster'},
    'Europe/Gibraltar': {'country': 'Gibraltar', 'subcountry': 'N/A'},
    'Europe/Helsinki': {'country': 'Finland', 'subcountry': 'Uusimaa'},
    'Europe/Kaliningrad': {'country': 'Russia',
                           'subcountry': 'Kaliningrad'},
    'Europe/Kiev': {'country': 'Ukraine', 'subcountry': 'Kyiv City'},
    'Europe/Kirov': {'country': 'Russia', 'subcountry': 'Murmansk'},
    'Europe/Lisbon': {'country': 'Portugal', 'subcountry': 'Lisbon'},
    'Europe/London': {'country': 'Canada', 'subcountry': 'Ontario'},
    'Europe/Luxembourg': {'country': 'Luxembourg',
                          'subcountry': 'Luxembourg'},
    'Europe/Madrid': {'country': 'Colombia',
                      'subcountry': 'Cundinamarca'},
    'Europe/Minsk': {'country': 'Belarus', 'subcountry': 'Minsk City'},
    'Europe/Monaco': {'country': 'Monaco', 'subcountry': None},
    'Europe/Moscow': {'country': 'Russia', 'subcountry': 'Moscow'},
    'Europe/Oslo': {'country': 'Norway', 'subcountry': 'Oslo'},
    'Europe/Paris': {'country': 'France',
                     'subcountry': 'Ile-de-France'},
    'Europe/Prague': {'country': 'Czech Republic',
                      'subcountry': 'Praha'},
    'Europe/Riga': {'country': 'Latvia', 'subcountry': 'Riga'},
    'Europe/Rome': {'country': 'Italy', 'subcountry': 'Latium'},
    'Europe/Samara': {'country': 'Russia', 'subcountry': 'Samara'},
    'Europe/Saratov': {'country': 'Russia', 'subcountry': 'Saratov'},
    'Europe/Simferopol': {'country': 'Ukraine',
                          'subcountry': 'Crimea'},
    'Europe/Sofia': {'country': 'Bulgaria',
                     'subcountry': 'Sofia-Capital'},
    'Europe/Stockholm': {'country': 'Sweden',
                         'subcountry': 'Stockholm'},
    'Europe/Tallinn': {'country': 'Estonia', 'subcountry': 'Harjumaa'},
    'Europe/Ulyanovsk': {'country': 'Russia', 'subcountry': 'Ulyanovsk'},
    'Europe/Vienna': {'country': 'Austria', 'subcountry': 'Vienna'},
    'Europe/Vilnius': {'country': 'Lithuania',
                       'subcountry': 'Vilnius County'},
    'Europe/Volgograd': {'country': 'Russia', 'subcountry': 'Volgograd'},
    'Europe/Warsaw': {'country': 'Poland',
                      'subcountry': 'Masovian Voivodeship'},
    'Europe/Zurich': {'country': 'United States',
                      'subcountry': 'Illinois'},
    'Indian/Mahe': {'country': 'India',
                    'subcountry': 'Madhya Pradesh'},
    'Pacific/Apia': {'country': 'Brazil', 'subcountry': 'Sao Paulo'},
    'Pacific/Auckland': {'country': 'United Kingdom',
                         'subcountry': 'England'},
    'Pacific/Chatham': {'country': 'United Kingdom',
                        'subcountry': 'England'},
    'Pacific/Funafuti': {'country': 'Tuvalu', 'subcountry': 'Funafuti'},
    'Pacific/Gambier': {'country': 'Australia',
                        'subcountry': 'South Australia'},
    'Pacific/Guam': {'country': 'Brazil', 'subcountry': 'Pará'},
    'Pacific/Honolulu': {'country': 'United States',
                         'subcountry': 'Hawaii'},
    'Pacific/Majuro': {'country': 'Marshall Islands',
                       'subcountry': 'Majuro Atoll'},
    'Pacific/Norfolk': {'country': 'Canada', 'subcountry': 'Ontario'},
    'Pacific/Pago_Pago': {'country': 'American Samoa',
                          'subcountry': 'Eastern District'},
    'Pacific/Palau': {'country': 'Mexico', 'subcountry': 'Coahuila'},
    'Pacific/Port_Moresby': {'country': 'Papua New Guinea',
                             'subcountry': 'National Capital'},
    'Pacific/Tarawa': {'country': 'Kiribati',
                       'subcountry': 'Gilbert Islands'},
    'Pacific/Wake': {'country': 'United Kingdom', 'subcountry': 'England'},
}
CONTINENTS = ['Africa', 'America', 'Antarctica', 'Asia',
              'Australia', 'Europe', 'Indian', 'Pacific']
CITY_NAME_KEY = "name"
COUNTRY_NAME_KEY_IN_CONTITNENTS = "Country_Name"
COUNTRY_NAME_KEY_IN_CITIES = "country"
SUBCOUNTRY_NAME_KEY_IN_CITIES = "subcountry"
CONTINENT_NAME_KEY = "Continent_Name"
CONTINENT = 'continent'
COUNTRY = 'country'
PLACE = 'place'
CURRENT_TIME_KEY = 'datetime'
TIMEZONE_PARTS_MAP = {CONTINENT: 0, PLACE: -1}
TIME_SCOPE_INDEX = 0
FEEDBACK_INDEX = 1
ARB_COUNTRY_TIMEZONE = -1
PATH_SEPARETOR = '/'
PARTS_OF_THE_DAY_FEEDBACK = {'Early morning':
                             [('05:00:00', '07:59:59'), 'Better not'],
                             'Morning':
                             [('08:00:00', '10:59:59'), 'OK'],
                             'Late morning':
                             [('11:00:00', '11:59:59'), 'OK'],
                             'Early afternoon':
                             [('12:00:00', '12:59:59'), 'OK'],
                             'Afternoon':
                             [('13:00:00', '15:59:59'), 'OK'],
                             'Late afternoon':
                             [('16:00:00', '16:59:59'),
                                  'Can be considered'],
                             'Early evening':
                             [('17:00:00', '18:59:59'),
                                  'Can be considered'],
                             'Evening':
                             [('19:00:00', '20:59:59'), 'Better not'],
                             'Night':
                             [('21:00:00', '23:59:59'), 'Better not'],
                             'Late night':
                             [('00:00:00', '04:59:59'),
                                  'Not possible'], }


def normalize_continent_name(continent_name: str) -> Optional[str]:
    """Normalize a given continent name to the continent name
       that appears in the timezone list.


    Args:
        continent_name (str): The given continent name.


    Returns:
        str: The normalized continent name.
    """
    for continent in CONTINENTS:
        if continent in continent_name:
            return continent
    return continent_name


def get_continent(country_name: str) -> Optional[str]:
    """Get the continent of a given country.


    Args:
        country_name (str): The given country name.


    Returns:
        str: The suitable continent name.
    """
    details = requests.get(COUNTRY_TO_CONTINENT_DATA_SET).json()
    for country_element in details:
        if country_name.title() in \
                country_element[COUNTRY_NAME_KEY_IN_CONTITNENTS]:
            return normalize_continent_name(
                country_element[CONTINENT_NAME_KEY])


def get_country(city_name: str) -> Optional[str]:
    """Get the country of a city.


    Args:
        city_name (str): The given city name.


    Returns:
        str: The suitable country name.
    """
    details = requests.get(CITY_TO_COUNTRY_DATA_SET).json()
    for city_element in details:
        if city_name.title() in city_element[CITY_NAME_KEY].title():
            return city_element[COUNTRY_NAME_KEY_IN_CITIES]


def get_subcountry(city_name: str) -> Optional[str]:
    """Get the subcountry of a city.


    Args:
        city_name (str): The given city name.


    Returns:
        str: The suitable subcountry name.
    """
    details = requests.get(CITY_TO_COUNTRY_DATA_SET).json()
    for city_element in details:
        if city_name.title() in city_element[CITY_NAME_KEY].title():
            return city_element[SUBCOUNTRY_NAME_KEY_IN_CITIES]


def get_api_data(url: str) -> Optional[List[str]]:
    """Get the data from an API url.

    Args:
        url (str):  The API url.

    Returns:
        list: The data.
    """
    try:
        resp = requests.get(url)
        return resp.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)


def parse_timezones_list() -> List[Tuple[str, ...]]:
    """Parse the timezones list into pairs of continent-place.


    Returns:
        list: The parsed data.
    """
    timezones_list = get_api_data(TIMEZONES_BASE_URL)
    return [tuple(timezone.split(PATH_SEPARETOR)) for
            timezone in timezones_list]


def get_timezones_parts(part: str) -> List[str]:
    """Get a given part of the timezones.

    Args:
        part (str):  The given part.

    Returns:
        list: a list of the relevant parts of the timezones list.
    """
    parse_list = parse_timezones_list()
    return [timezone[TIMEZONE_PARTS_MAP[part]] for timezone in parse_list]


def standardize_country_or_place(place_name: str) -> str:
    """Standardize a given country or place name to the equivalent
       name that appears in the timezone list.


    Args:
        place_name (str): The given country or place name.


    Returns:
        str: The standardized name.
    """
    if place_name:
        return place_name.replace(BLANK, UNDERSCORE).title()


def standardize_continent(continent_name: str) -> str:
    """Standardize a given continent name to the equivalent name that
       appears in the timezone list.


    Args:
        continent_name (str): The given continent name.


    Returns:
        str: The standardized name.
    """
    if continent_name in get_timezones_parts(CONTINENT):
        return continent_name


def search_timezone_by_just_place(place_name: str) -> Optional[str]:
    """Search for a timezone in the timezones list by a given place name.


    Args:
        place_name (str): The given place name.


    Returns:
        str: The suitable timezone.
    """
    res = [timezone for timezone in get_api_data(TIMEZONES_BASE_URL)
           if place_name in timezone]
    if len(res):
        return res[UNPACK_ELEMENT]


def generate_possible_timezone_path(map_hierarchy: Dict[str, Optional[str]]
                                    ) -> List[Optional[str]]:
    """Generate all possible timezone paths, given a map hierarchy
       of continent -> country -> place.


    Args:
        map_hierarchy (dict): The hierarchy details.


    Returns:
        list: The list of possible timezones.
    """
    prefix = map_hierarchy[CONTINENT]
    possibilities = [f"{prefix}/{map_hierarchy[COUNTRY]}",
                     f"{prefix}/{map_hierarchy[PLACE]}"]
    return possibilities


def get_all_possible_timezone_paths_for_given_place(place_name: str)\
        -> Optional[List[str]]:
    """Get all possible timezone paths for given place.


    Args:
        place_name (str): The given place name.


    Returns:
        list: The list of possible timezones.
    """
    map_hierarchy = {CONTINENT: None, COUNTRY: None, PLACE: None, }
    possibilities = []
    country = get_country(place_name)
    country = standardize_country_or_place(country)
    if country:
        map_hierarchy[COUNTRY] = country
        map_hierarchy[PLACE] = place_name
        continent = get_continent(country)
        continent = standardize_continent(continent)
        map_hierarchy[CONTINENT] = continent

        if not continent:
            if country in get_timezones_parts(PLACE):
                possibilities.append(search_timezone_by_just_place(country))
                return possibilities
        else:
            return possibilities + generate_possible_timezone_path(
                map_hierarchy)
    continent = get_continent(place_name)
    continent = standardize_continent(continent)
    if not continent:
        place_name = standardize_country_or_place(place_name)
        if place_name in get_timezones_parts('place'):
            possibilities.append(search_timezone_by_just_place(place_name))
            return possibilities
    return possibilities.append(f"{continent}/{place_name}")


def get_timezone_path_for_given_place(place_name: str) -> Optional[str]:
    """Get a timezone path for a given place.


    Args:
        place_name (str): The given place name.


    Returns:
        str: The timezone path.
    """
    possibilities = \
        get_all_possible_timezone_paths_for_given_place(place_name)
    timezones_list = get_api_data(TIMEZONES_BASE_URL)
    if possibilities:
        for possibility in possibilities:
            if possibility in timezones_list:
                return f'{TIMEZONES_BASE_URL}/{possibility}'
    # NO EXPLICIT SUCH TIMEZONES. GET ARBITRARY TIMEZONE OF COUNTRY
    if standardize_continent(place_name.title()):
        continent_url = f'{TIMEZONES_BASE_URL}/{place_name}'
        api_data = get_api_data(continent_url)
        timezone = api_data[ARB_COUNTRY_TIMEZONE]
        return f'{TIMEZONES_BASE_URL}/{timezone}'
    subcountry = get_subcountry(place_name)
    country = get_country(place_name)
    if subcountry:
        for timezone, details in TIMEZONES_COUNTRY_SUBCOUNTRY.items():
            if details[SUBCOUNTRY_NAME_KEY_IN_CITIES] == \
                    subcountry or details[COUNTRY] == country:
                return f'{TIMEZONES_BASE_URL}/{timezone}'


def get_current_time_in_place(place_name: str) -> Optional[str]:
    """Get the current time in a given place.


    Args:
        place_name (str): The given place name.


    Returns:
        str: The timezone path.
    """
    path = get_timezone_path_for_given_place(place_name)
    if path:
        current_datetime_details = get_api_data(path)
        current_datetime_full = current_datetime_details[CURRENT_TIME_KEY]
        current_datetime_parsed = \
            dateutil.parser.parse(current_datetime_full)
        current_time = current_datetime_parsed.strftime('%H:%M:%S')
        return current_time


def get_part_of_day_and_feedback(time: datetime) -> Tuple[str, str]:
    """Get the part of day and a suitable feedback for a given time.


    Args:
        time (datetime): The given time.


    Returns:
        tuple: The part of day description and the feedback.
    """
    for part_of_day, details in PARTS_OF_THE_DAY_FEEDBACK.items():
        start_time_scope, end_time_scope = details[TIME_SCOPE_INDEX]
        feedback = details[FEEDBACK_INDEX]
        if time >= datetime.strptime(start_time_scope, '%H:%M:%S') \
                and time <= datetime.strptime(end_time_scope, '%H:%M:%S'):
            return part_of_day, feedback


def meeting_possibility_feedback(time_str: str, place_name: str) \
        -> Tuple[str, str, str]:
    """Get the equivalent time in a given place,
       the part of the day of that time and a feedback.


    Args:
        time_str (str): The given time as string in format HH:MM:SS.
        place_name (str): The given place name.


    Returns:
        tuple: The equivalent time in the given place,
               the part of the day of that time and a feedback.
    """
    now = datetime.now()
    time_now_str = now.strftime("%H:%M:%S")
    time_now = datetime.strptime(time_now_str, "%H:%M:%S")
    input_time = datetime.strptime(time_str, "%H:%M:%S")
    current_time_in_place = get_current_time_in_place(place_name)
    if current_time_in_place:
        current_time_in_place = \
            datetime.strptime(current_time_in_place, '%H:%M:%S')
        delta_in_hours = \
            int((time_now - current_time_in_place).total_seconds()
                / TOTAL_SEC_IN_HOUR)
        attendance_time = (input_time + timedelta(hours=delta_in_hours)).\
            strftime('%H:%M:%S')
        attendance_time = datetime.strptime(attendance_time, "%H:%M:%S")
        part_of_day, feedback = \
            get_part_of_day_and_feedback(attendance_time)
        return f"{attendance_time.strftime('%H')}:" \
               f"{datetime.strftime(input_time, '%M:%S')}", \
               part_of_day, feedback
