from contextlib import contextmanager

from leapc_cffi import ffi, libleapc

from .datatypes import LeapCStruct
from .enums import get_enum_entries, DevicePID, DeviceStatus
from .exceptions import success_or_raise, LeapError, LeapCannotOpenDeviceError


class DeviceNotOpenException(LeapError):
    pass


class DeviceStatusInfo:
    def __init__(self, status: ffi.CData):
        """Create the DeviceStatusInfo

        :param status: The CData defining the status
        """
        self._status_flags = get_enum_entries(DeviceStatus, status)

    @staticmethod
    def _get_flags(status_int):
        return get_enum_entries(DeviceStatus, status_int)

    def check(self, flag: DeviceStatus):
        """Check if the flag is in the current flags

        :param flag: The flag to check
        """
        return flag in self._status_flags

    @property
    def flags(self):
        return self._status_flags


class DeviceInfo(LeapCStruct):
    @property
    def status(self):
        return DeviceStatusInfo(self._data.status)

    @property
    def caps(self):
        # TODO: Implement properly as flags
        return self._data.caps

    @property
    def pid(self):
        return DevicePID(self._data.pid)

    @property
    def baseline(self):
        return self._data.baseline

    @property
    def serial(self):
        return ffi.string(self._data.serial).decode("utf-8")

    @property
    def fov(self):
        """Get the horizontal & vertical field of view in radians"""
        return self._data.h_fov, self._data.v_fov

    @property
    def range(self):
        """Get the maximum range of this device, in micrometres"""
        return self._data.range


class Device:
    def __init__(self, device_ref=None, *, device=None, owner=None):
        """A Device is usually constructed from a LEAP_DEVICE_REF object.

        Some functions require the device to be opened before they can be
        called.

        If a DeviceLost event occurs, this can be created from a LEAP_DEVICE
        object. In this case the Device is already open and does not need to
        be closed by the user.

        The 'owner' argument is a CFFI object that must be kept alive
        for the device ref to remain valid. It should never be used from
        within the class.
        """
        self._device_ref = device_ref
        self._device = device
        self._owner = owner

    @property
    def c_data_device_ref(self):
        """Get the LEAP_DEVICE_REF object for this object"""
        return self._device_ref

    @property
    def c_data_device(self):
        """Get the LEAP_DEVICE object for this object

        If the device is not open, returns None
        """
        return self._device

    @property
    def id(self):
        if self._device_ref is None:
            # The device must have been returned from a DeviceLostEvent
            # This means it does not have an id, so return None
            return
        return self._device_ref.id

    @contextmanager
    def open(self):
        if self._device is not None:
            raise LeapCannotOpenDeviceError("Device is already open")

        device_ptr = ffi.new("LEAP_DEVICE*")
        success_or_raise(libleapc.LeapOpenDevice, self._device_ref, device_ptr)
        self._device = device_ptr[0]
        try:
            yield self
        finally:
            self._device = None
            libleapc.LeapCloseDevice(device_ptr[0])

    def get_info(self):
        """Get a DeviceInfo object containing information about this device

        Requires the Device to be open.
        Raises DeviceNotOpenException if the device is not open.
        """
        if self._device is None:
            raise DeviceNotOpenException()
        info_ptr = ffi.new("LEAP_DEVICE_INFO*")
        info_ptr.size = ffi.sizeof(info_ptr[0])
        info_ptr.serial = ffi.NULL
        success_or_raise(libleapc.LeapGetDeviceInfo, self._device, info_ptr)
        info_ptr.serial = ffi.new("char[]", info_ptr.serial_length)
        success_or_raise(libleapc.LeapGetDeviceInfo, self._device, info_ptr)
        return DeviceInfo(info_ptr[0])

    def get_camera_count(self):
        if not self._device:
            raise DeviceNotOpenException()
        camera_count_ptr = ffi.new("uint8_t *")
        success_or_raise(libleapc.LeapGetDeviceCameraCount, self._device, camera_count_ptr)
        return camera_count_ptr[0]
