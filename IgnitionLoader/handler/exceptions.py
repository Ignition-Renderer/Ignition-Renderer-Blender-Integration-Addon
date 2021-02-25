class BaseIgnitionException(Exception):
    pass


class BaseIgnitionWarning(Warning):
    pass

class NotAnIgnitionFile(BaseIgnitionException):
    '''Raised when the specified file is not a .ignition file'''

