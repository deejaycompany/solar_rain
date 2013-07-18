from interface import BaseVMException


class FailedException(BaseVMException):
    """
    There's a my custom exception that tells users about reasons of epic
    fails.
    """

    def __init__(self, message):
        super(FailedException, self).__init__(message)
        self.message = "Failed! Reason: " + message
