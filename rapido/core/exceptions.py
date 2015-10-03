class NotAllowed(Exception):
    pass


class Unauthorized(Exception):
    pass


class NotFound(Exception):

    def __init__(self, name):
        self.name = name
