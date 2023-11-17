from leapc_cffi import ffi


class LeapCStruct:
    """Base class for objects which wrap around some raw C Data

    Classes which inherit from this should only be loose wrappers around
    some struct from the LeapC API.

    :param data: The raw CData
    """

    def __init__(self, data: ffi.CData):
        self._data = data

    @property
    def c_data(self) -> ffi.CData:
        """Get the raw C data"""
        return self._data
