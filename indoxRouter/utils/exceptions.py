# utils/exceptions.py
class IndoxError(Exception):
    pass


class RateLimitError(IndoxError):
    pass


class ModelNotFoundError(IndoxError):
    pass
