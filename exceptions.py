"""Custom exceptions."""


class EnvironmentVariableError(Exception):
    """One of the nesessary environmental variables is missing."""


class ResponseError(Exception):
    """Got unexpected response from Практикум.Домашка."""


class SendMessageError(Exception):
    """Failed to send a message in telegram."""
