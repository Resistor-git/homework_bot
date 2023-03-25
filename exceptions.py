"""Custom exceptions."""


class EnvironmentVariableException(Exception):
    """One of the nesessary environmental variables is missing."""

    pass


class ResponseException(Exception):
    """Got unexpected response from Практикум.Домашка."""

    pass
