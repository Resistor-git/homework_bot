"""
Telegram bot 'practicum_review_status_bot'.

Checks the status of homework code review and sends a message in telegram if
status has changed.
"""

import os
import time
import sys
import requests
import logging
from http import HTTPStatus
from typing import Dict, Union

import telegram
from dotenv import load_dotenv

from exceptions import EnvironmentVariableError, ResponseError

load_dotenv()

PRACTICUM_TOKEN: str = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID')
RETRY_PERIOD: int = 600
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: Dict[str, str] = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_VERDICTS: Dict[str, str] = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# formatter = logging.Formatter(
#     '%(asctime)s [%(levelname)s] - %(message)s'
# )
# handler.setFormatter(formatter)
# logger.addHandler(handler)


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
                f'Environment variable {variable} not found. '
                'Program stopped.'
            )


def send_message(bot, message):
    """Send message to the chat with id == TELEGRAM_CHAT_ID."""
    logger.debug('send_message started')
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message)
    except Exception:
        logger.exception("Couldn't send a message in telegram.")
        raise Exception(
            "Couldn't send a message in telegram."
        )
    else:
        logger.debug(f'Message "{message}" sent in chat {TELEGRAM_CHAT_ID}')


def get_api_answer(timestamp):
    """Get info about homeworks since the date in the timestamp."""
    logger.debug('get_api_answer started')
    request_args: Dict[str, Union[str, dict]] = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp}
    }
    try:
        response: requests.models.Response = requests.get(**request_args)
        if response.status_code != HTTPStatus.OK:
            # logger.exception('Endpoint returned unexpected status code')
            raise ResponseError(
                f'Unexpected status code in response: {response.status_code}\n'
                f'Response: {response.text}'
                f'Request url: {request_args.get("url")}\n'
                f'Request headers: {request_args.get("headers")}\n'
                f'Request params: {request_args.get("params")}'
            )
        return response.json()
    except requests.RequestException:
        # logger.exception('Unexpected answer from API.')
        raise requests.RequestException(
            'Unexpected answer from API.'
        )


def check_response(response):
    """Ensure that response from Практикум.Домашка has nesessary info."""
    logger.debug('check_response started')
    if not isinstance(response, dict):
        logger.exception(
            'Got unexpected response from Практикум.Домашка. '
            'Response is not dict.'
        )
        raise TypeError(
            'Got unexpected response from Практикум.Домашка. '
            'Response is not dict.'
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
        homework_name: str = homework['homework_name']
        status: str = homework['status']
        verdict = HOMEWORK_VERDICTS[status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except KeyError as error:
        logger.exception(
            'Unexpected key. Probably unexpected status of the homework.\n'
            f'{error}')
        raise KeyError(
            'Unexpected key. Probably unexpected status of the homework.'
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
            message = parse_status(api_answer['homeworks'][0])
            if message != last_message:
                send_message(bot, message)
                last_message = message
            else:
                logger.debug('Homework status did not change')
        except (ResponseError,
                requests.RequestException,
                IndexError,
                KeyError,
                TypeError) as error:
            error_message = f'Program failure: {error}'
            logger.exception(error_message)
            if last_error_message != error_message:
                bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=error_message
                )
            logger.debug(f'Bot sent message: "{error_message}"')
            last_error_message = error_message
        except Exception as error:
            logger.exception(f'Something went wrong: {error}')
            error_message = f'Program failure: {error}'
            if last_error_message != error_message:
                bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=error_message
                )
                logger.debug(f'Bot sent message: "{error_message}"')
                last_error_message = error_message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    # logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] - %(message)s.\n'
        'File "%(filename)s" - line %(lineno)d - func "%(funcName)s"'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    main()
