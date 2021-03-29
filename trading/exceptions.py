from rest_framework.exceptions import APIException


class TradingException(APIException):
    pass


class InvalidOrderException(APIException):
    status_code = 400
    default_detail = "Invalid order - insufficient funds or shares."
    default_code = "invalid_order"


class InsufficienFundsException(APIException):
    status_code = 400
    default_detail = "Insufficient funds"
    default_code = "insufficient_funds"


class InsufficienSharesException(APIException):
    status_code = 400
    default_detail = "Insufficient shares"
    default_code = "insufficient_shares"
