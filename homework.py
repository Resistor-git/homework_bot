import os
import time
import requests
import logging
from http import HTTPStatus
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
        logger.debug(f'Message "{message}" sent in chat {TELEGRAM_CHAT_ID}')
    except Exception:
        logger.exception("Couldn't send a message in telegram.")


def get_api_answer(timestamp):
    """Get info about homeworks since the date in the timestamp."""
    logger.debug('get_api_answer started')
    date: Dict[str, int] = {'from_date': timestamp}
    try:
        response: requests.models.Response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=date
        )
        if response.status_code != HTTPStatus.OK:
            logger.exception('Endpoint returned unexpected status code')
            raise ResponseError(
                f'Unexpected status code in response: {response.status_code}'
            )
        return response.json()
    except requests.exceptions.RequestException:
        logger.exception('Unexpected answer from API.')


def check_response(response):
    """
    Ensure that response from Практикум.Домашка has nesessary info
    and there is a least one homerwork.
    """
    logger.debug('check_response started')
    if not isinstance(response, dict):
        logger.exception(
            'Got unexpected response from Практикум.Домашка. '
            'Response in not dict.'
        )
        raise TypeError(
            'Got unexpected response from Практикум.Домашка. '
            'Response in not dict.'
        )
    elif not ('current_date' and 'homeworks' in response.keys()):
        logger.exception(
            'No information about current date and homeworks in API response'
        )
        raise ResponseError(
            'Got unexpected response from Практикум.Домашка'
        )
    elif not isinstance(response['homeworks'], list):
        logger.exception(
            'Got unexpected response from Практикум.Домашка. '
            'Homeworks should be a list.'
        )
        raise TypeError(
            'Got unexpected response from Практикум.Домашка. '
            'Homeworks should be a list.'
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
        raise IndexError(
            "Couldn't find the homework."
        )
    except KeyError as error:
        logger.exception(
            'Unexpected key. Probably unexpected status of the homework.\n'
            f'{error}')
        raise KeyError(
            'Unexpected key. Probably unexpected status of the homework.'
        )
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
    last_message: str = ''
    last_error_message: str = ''

    while True:
        try:
            api_answer = get_api_answer(timestamp)
            check_response(api_answer)
            message = parse_status(api_answer)
            if message != last_message:
                send_message(bot, message)
                last_message = message
            else:
                logger.debug('Homework status did not change')
            # time.sleep(RETRY_PERIOD)
        except (ResponseError,
                requests.exceptions.RequestException,
                IndexError,
                KeyError,
                TypeError) as error:
            message = f'Error: {error}'
            if last_error_message != message:
                error_message = bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=message
                )
                last_error_message = message
            logger.debug(f'Bot sent message: "{error_message.text}"')
            last_error_message = error_message.text
            # time.sleep(5)
        except Exception as error:
            logger.exception(f'Something went wrong: {error}')
            message = f'Сбой в работе программы: {error}'
            if last_error_message != message:
                error_message = bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=message
                )
                last_error_message = message
            # time.sleep(RETRY_PERIOD)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
