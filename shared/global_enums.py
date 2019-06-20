import enum
import logging
from enum import Enum

import config

LOG = logging.getLogger(config.LOG_BASE_NAME + '.' + __name__)

# By extending "str" it becomes json serializable
class StrEnum(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
    def __str__(self):
        return str(self.name)
    def __format__(self):
        return self.__str__()

class RequestType(StrEnum):
    NORMAL = enum.auto()
    STATIC = enum.auto()


class UserMessageTypes(StrEnum):
    DEFAULT = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()
    SUCCESS = enum.auto()


class ErrorCode(StrEnum):
    # 400
    BAD_REQUEST = enum.auto()
    MALFORMED_ENTITY = enum.auto()
    # 401
    NO_AUTHORIZATION = enum.auto()
    WRONG_AUTH = enum.auto()
    # 403
    NOT_AUTHORIZED = enum.auto()
    # 404
    NOT_FOUND = enum.auto()
    # 415
    FILE_TYPE_NOT_SUPPORTED = enum.auto()
    # 422
    INCOHERENT_DATA = enum.auto()
    # 500
    UNEXPECTED_ERROR = enum.auto()
    # 501
    NOT_IMPLEMENTED = enum.auto()


