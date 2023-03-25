import os
import time
import requests
from typing import Dict
from pprint import pprint

import telegram
from dotenv import load_dotenv

from exceptions import EnvironmentVariableException, ResponseException

load_dotenv()

PRACTICUM_TOKEN: str = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID')
RETRY_PERIOD: int = 600
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: str = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_VERDICTS: Dict[str, str] = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    if not (PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID):
        raise EnvironmentVariableException(
            'One or more of environment variables missing.'
        )


def send_message(bot, message):
    ...


def get_api_answer(timestamp):
    """Get info about homeworks since the date in the timestamp."""
    date: Dict[str, int] = {'from_date': timestamp}
    response: requests.models.Response = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=date
    )
    return response


def check_response(response):
    """Ensure that response from Практикум.Домашка has nesessary info."""
    if not ('current_date' and 'homeworks' in response.keys()):
        raise ResponseException(
            'Got unexpected response from Практикум.Домашка'
        )


def parse_status(homework):
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    ...

    bot: telegram.Bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp: int = int(time.time())
    ...
    get_api_answer(timestamp)
    # check_response(get_api_answer(timestamp))

    while True:
        try:

            ...

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()
