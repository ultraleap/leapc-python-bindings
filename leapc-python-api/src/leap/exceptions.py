"""Exceptions which are available in the LeapC API"""

from .enums import RS as LeapRS


class LeapError(Exception):
    pass


class LeapConnectionAlreadyOpen(LeapError):
    pass


# All following Exceptions are translated from the LeapRS enum


class LeapUnknownError(LeapError):
    pass


class LeapInvalidArgumentError(LeapError):
    pass


class LeapInsufficientResourcesError(LeapError):
    pass


class LeapInsufficientBufferError(LeapError):
    pass


class LeapTimeoutError(LeapError):
    pass


class LeapNotConnectedError(LeapError):
    pass


class LeapHandshakeIncompleteError(LeapError):
    pass


class LeapBufferSizeOverflowError(LeapError):
    pass


class LeapProtocolError(LeapError):
    pass


class LeapInvalidClientIDError(LeapError):
    pass


class LeapUnexpectedClosedError(LeapError):
    pass


class LeapUnknownImageFrameRequestError(LeapError):
    pass


class LeapRoutineIsNotSeerError(LeapError):
    pass


class LeapTimestampTooEarlyError(LeapError):
    pass


class LeapConcurrentPollError(LeapError):
    pass


class LeapNotAvailableError(LeapError):
    pass


class LeapNotStreamingError(LeapError):
    pass


class LeapCannotOpenDeviceError(LeapError):
    pass


def create_exception(result: LeapRS, *args, **kwargs):
    """Create an exception from a LeapRS object

    Extra args and kwargs are forwarded to the Exception constructor.

    :param result: The result to create an Exception from
    """
    if result == LeapRS.Success:
        raise ValueError("Success is not an Error")

    _ERRORS = {
        LeapRS.UnknownError: LeapUnknownError,
        LeapRS.InvalidArgument: LeapInvalidArgumentError,
        LeapRS.InsufficientResources: LeapInsufficientResourcesError,
        LeapRS.InsufficientBuffer: LeapInsufficientBufferError,
        LeapRS.Timeout: LeapTimeoutError,
        LeapRS.NotConnected: LeapNotConnectedError,
        LeapRS.HandshakeIncomplete: LeapHandshakeIncompleteError,
        LeapRS.BufferSizeOverflow: LeapBufferSizeOverflowError,
        LeapRS.ProtocolError: LeapProtocolError,
        LeapRS.InvalidClientID: LeapInvalidClientIDError,
        LeapRS.UnexpectedClosed: LeapUnexpectedClosedError,
        LeapRS.UnknownImageFrameRequest: LeapUnknownImageFrameRequestError,
        LeapRS.RoutineIsNotSeer: LeapRoutineIsNotSeerError,
        LeapRS.TimestampTooEarly: LeapTimestampTooEarlyError,
        LeapRS.ConcurrentPoll: LeapConcurrentPollError,
        LeapRS.NotAvailable: LeapNotAvailableError,
        LeapRS.NotStreaming: LeapNotStreamingError,
        LeapRS.CannotOpenDevice: LeapCannotOpenDeviceError,
    }

    return _ERRORS[result](args, kwargs)


def success_or_raise(func, *args):
    """Call the function with the args, and raise an exception if the result is not success

    The function must be a LeapC cffi function which returns a LeapRS object.
    """
    result = LeapRS(func(*args))
    if result != LeapRS.Success:
        raise create_exception(result)
