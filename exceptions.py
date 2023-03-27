"""Custom exceptions."""


class EnvironmentVariableError(Exception):
    """One of the nesessary environmental variables is missing."""


class ResponseError(Exception):
    """Got unexpected response from Практикум.Домашка."""
