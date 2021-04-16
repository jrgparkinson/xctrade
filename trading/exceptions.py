from rest_framework.exceptions import APIException


class TradingException(APIException):
    """ General app exception """

    error: str

    def __init__(self, error):
        super().__init__()
        self.error = error

    def __str__(self):
        return f"TradingException: {self.error}"


class InvalidOrderException(APIException):
    """Order is not valid"""

    status_code = 400
    default_detail = "Invalid order - insufficient funds or shares."
    default_code = "invalid_order"


class InsufficienFundsException(APIException):
    """ Insufficient funds """

    status_code = 400
    default_detail = "Insufficient funds"
    default_code = "insufficient_funds"


class InsufficienSharesException(APIException):
    """ Insufficient shares """

    status_code = 400
    default_detail = "Insufficient shares"
    default_code = "insufficient_shares"
