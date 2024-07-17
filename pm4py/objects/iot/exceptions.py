class UnexpectedStateError(Exception):
    """raised for non-existent state"""

    def __str__(self):
        return f'{self.fname} non existent state={self.state}'
    def __init__(self, fname, state):
        self.fname = fname.__name__
        self.state = state


class UnexpectedAttributeError(Exception):
    """raised for unexpected attribute types"""

    def __str__(self):
        return f'{self.name} unexpected attribute type, attr = {self.attr}, type = {type(self.attr)}'
    def __init__(self, name, attr):
        self.name = name
        self.attr = attr


class InvalidAttributeError(Exception):
    """raised for not supported attributes"""

    def __str__(self):
        return f'{self.name} attribute with key={self.key} and value={self.value} not supported'
    def __init__(self, name, key, value):
        self.name = name
        self.key = key
        self.value = value


class PresentAttributeError(Exception):
    """raised for already present attributes"""

    def __str__(self):
        return f'{self.name} attribute with key={self.key} and value={self.value} is already present'
    def __init__(self, name, key, value):
        self.name = name
        self.key = key
        self.value = value


class AttributeShouldBeNoneError(Exception):
    """raised for attributes which already have value"""

    def __str__(self):
        return f'expected {self.name} to be None, have {self.attr}'
    def __init__(self, name, attr):
        self.name = name
        self.attr = attr


class AttributeShouldNotBeNoneError(Exception):
    """raised for attributes which should not be None"""

    def __str__(self):
        return f'expected to have {self.name}'
    def __init__(self, name):
        self.name = name


class NestedAttributeShouldBeEmptyError(Exception):
    """raised for non-empty nested attributes"""

    def __str__(self):
        return f'expected {self.name} stack to be empty, have {self.attr}'
    def __init__(self, name, attr):
        self.name = name
        self.attr = attr


class NestedAttributeShouldNotBeEmptyError(Exception):
    """raised for empty nested attributes"""

    def __str__(self):
        return f'{self.name} stack is empty'
    def __init__(self, name):
        self.name = name


class UnexpectedMultipleLogError(Exception):
    """raised for multiple logs found"""
    def __str__(self):
        return f'unexpected to have multiple logs in one file'


class UnsupportedTypeError(Exception):
    """raised for invalid object"""
    def __str__(self):
        return f'Unsupported {self.type} object'
    def __init__(self, type):
        self.type = type


class VerificationFailedError(Exception):
    """raised for failed verification"""
    def __str__(self):
        return f'{self.type} verification failed: {self.msg}'
    def __init__(self, obj, msg):
        self.type = type(obj)
        self.msg = msg