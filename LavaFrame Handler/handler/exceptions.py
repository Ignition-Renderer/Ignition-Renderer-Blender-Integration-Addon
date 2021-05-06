class BaseIgnitionException(Exception):
    pass


class BaseIgnitionWarning(Warning):
    pass

class NotAnIgnitionFile(BaseIgnitionException):
    '''Raised when the specified file is not a .ignition file'''

class NotAnIgnitionNode(BaseIgnitionException):
    '''Raised when a material's output is not connected to an Ignition node'''