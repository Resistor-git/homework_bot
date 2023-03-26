import os
import time
import requests
import logging
from typing import Dict

import telegram
from dotenv import load_dotenv

from exceptions import EnvironmentVariableError, ResponseError

load_dotenv()
# !!!!!!!!!!!!!!!!
DEBUG_DATE = int(time.time()) - (60 * 60 * 24 * 20)
# !!!!!!!!!!!!!!!!!!!

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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Check that nesessary tokens are provided.

    By default nesessary tokens are:
    PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    """
    logger.debug('check_tokens started')
    expected_variables = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID}
    for variable in expected_variables:
        if not expected_variables[variable]:
            logger.critical(f'{variable} not found.')
            raise EnvironmentVariableError(
                f'Environment variable {variable} not found.'
            )


def send_message(bot, message):
    """Send message to the chat with id == TELEGRAM_CHAT_ID."""
    logger.debug('send_message started')
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message)
        logger.debug('Message sent')
    except Exception:
        logger.exception("Couldn't send a message in telegram.")


def get_api_answer(timestamp):
    """Get info about homeworks since the date in the timestamp."""
    logger.debug('get_api_answer started')
    date: Dict[str, int] = {'from_date': timestamp}
    response: requests.models.Response = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=date
    )
    if response.status_code == 404:
        logger.exception('Endpoint unavailable')
    elif response.status_code != 200:
        logger.exception('Endpoint returned unexpected status code')
    return response.json()


def check_response(response):
    """
    Ensure that response from Практикум.Домашка has nesessary info
    and there is a least one homerwork.
    """
    logger.debug('check_response started')
    if not ('current_date' and 'homeworks' in response.keys()):
        logger.exception(
            'No information about current date and homeworks in API response'
        )
        raise ResponseError(
            'Got unexpected response from Практикум.Домашка'
        )
    elif len(response['homeworks']) < 1:
        logger.exception('No homeworks found in the API response')
        raise ResponseError(
            'No homeworks found in response from Практикум.Домашка'
        )


def parse_status(homework):
    """Analyses the response from Практикум.Домашка."""
    logger.debug('parse_status started')
    try:
        last_homework: Dict = homework['homeworks'][0]
        homework_name: str = last_homework['homework_name']
        status: str = last_homework['status']
        verdict = HOMEWORK_VERDICTS[status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except IndexError:
        logger.exception("Couldn't find the homework.")
    except KeyError as error:
        logger.exception(
            'Unexpected key. Probably unexpected status of the homework.\n'
            f'{error}')
    except Exception as error:
        logger.exception(
            'Something went wrong during parsing of the response.\n'
            f'{error}'
        )


def main():
    """
    Ask Практикум.Домашка for status of homework (every 10 mins by default).
    If status has changed from the last request - sends a message in
    telegram.
    """
    logger.debug('main started')
    check_tokens()
    bot: telegram.Bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp: int = int(time.time())
    last_message = ''

    while True:
        try:
            api_answer = get_api_answer(timestamp)
            check_response(api_answer)
            message = parse_status(api_answer)
            if message != last_message:
                send_message(bot, message)
                last_message = message
                time.sleep(5)
            else:
                logger.debug('Homework status did not change')
        except ResponseError:
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()
