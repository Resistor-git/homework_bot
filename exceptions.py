"""Custom exceptions."""


class EnvironmentVariableError(Exception):
    """One of the nesessary environmental variables is missing."""

    pass


class ResponseError(Exception):
    """Got unexpected response from Практикум.Домашка."""

    pass
