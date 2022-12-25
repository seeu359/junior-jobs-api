class InvalidDateParams(Exception):
    pass


class DataAlreadyUploaded(Exception):
    """
    Data has been uploaded in database already today.
    """
    pass
