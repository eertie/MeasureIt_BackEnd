import decimal
import datetime
import traceback

from api import logger


class AppResponse:
    """
    Custom response class that represents the response of an application.
    Allows setting the response code, message, data, and error information.
    If an exception is provided, the code is set to 500 and the error message and stack trace are captured.
    """

    def __init__(self, code: int = 200, message: str = 'success', data: any = None, e: Exception = None):
        """
        Initializes an AppResponse object with the provided code, message, data, and exception.

        Args:
            code (int): The response code. Default is 200.
            message (str): The response message. Default is 'success'.
            data (any): Any data associated with the response. Default is None.
            e (Exception): An optional exception. Default is None.
        """
        self.code = code
        self.message = message
        self.data = data
        self.error_message = None
        self.stack_trace = None
        self.e = e
        if self.e:
            self.code = 500
            self.error_message = str(e)
            self.stack_trace = traceback.format_exc()
            # logger.error(str(e))
            logger.error(self.stack_trace)

    def __repr__(self):
        """
        Returns a string representation of the AppResponse object.
        """
        return f"AppResponse({self.code}, '{self.message}', {self.data}, '{self.error_message}')"

    def fullMessage(self):
        """
        Returns a dictionary containing the code, message, data, error message, and stack trace (if an exception is provided).
        """
        if self.e:
            return {
                'code': self.code,
                'message': self.message,
                'data': self.data,
                'error_message': self.error_message,
                'stack_trace': self.stack_trace
            }
        return {
            'code': self.code,
            'message': self.message,
            'data': self.data
        }


def jsonEncoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
