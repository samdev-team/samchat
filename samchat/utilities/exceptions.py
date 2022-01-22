class StreamTerminated(Exception):
    """A socket receive or send has stopped being able to send
    data because the connection to the socket has been terminated"""
    pass


class EncryptionFailed(Exception):
    """A wrong encryption key has been used"""
    pass
