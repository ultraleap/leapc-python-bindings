"""Classes for each of the LeapC Events

These are created so that the members can be accessed as our custom Python objects
instead of C Objects.
"""

from .cstruct import LeapCStruct
from .datatypes import FrameHeader, Hand, Vector, Image
from .device import Device, DeviceStatusInfo
from .enums import EventType, get_enum_entries, TrackingMode, PolicyFlag, IMUFlag
from leapc_cffi import ffi


class EventMetadata(LeapCStruct):
    def __init__(self, data):
        super().__init__(data)
        self._event_type = EventType(data.type)
        self._device_id = data.device_id

    @property
    def event_type(self):
        return self._event_type

    @property
    def device_id(self):
        return self._device_id


class Event(LeapCStruct):
    """Base class for Events

    Events have extra 'type' and 'metadata' properties.

    If the Event is constructed using the default constructor, the metadata is not populated.

    If the event is constructed using a `LEAP_CONNECTION_MESSAGE*` via the
    `from_connection_message` method, extra metadata will be available on
    the event.
    """

    # The type of event this class corresponds to
    _EVENT_TYPE = EventType.EventTypeNone
    # The member on the `LEAP_CONNECTION_MESSAGE` that corresponds to the
    # event data.
    _EVENT_MESSAGE_ATTRIBUTE = "pointer"

    def __init__(self, data):
        super().__init__(data)
        self._metadata = None

    @classmethod
    def from_connection_message(cls, c_message):
        """Construct an Event from a LEAP_CONNECTION_MESSAGE* object

        Constructing an event in this way populates the event metadata.
        """
        if EventType(c_message.type) != cls._EVENT_TYPE:
            raise ValueError("Incorect event type")

        event = cls(getattr(c_message, cls._EVENT_ATTRIBUTE))
        event._metadata = EventMetadata(c_message)
        return event

    @classmethod
    def _get_event_cdata(cls, c_message):
        return getattr(c_message, cls._EVENT_ATTRIBUTE)

    @property
    def metadata(self):
        return self._metadata

    @property
    def type(self):
        return self._EVENT_TYPE


class NoneEvent(Event):
    _EVENT_TYPE = EventType.EventTypeNone
    _EVENT_ATTRIBUTE = "pointer"


class ConnectionEvent(Event):
    _EVENT_TYPE = EventType.Connection
    _EVENT_ATTRIBUTE = "connection_event"


class ConnectionLostEvent(Event):
    _EVENT_TYPE = EventType.ConnectionLost
    _EVENT_ATTRIBUTE = "connection_lost_event"


class DeviceEvent(Event):
    _EVENT_TYPE = EventType.Device
    _EVENT_ATTRIBUTE = "device_event"

    def __init__(self, data):
        super().__init__(data)
        self._device = Device(data.device)
        self._status = DeviceStatusInfo(data.status)

    @property
    def device(self):
        return self._device

    @property
    def status(self):
        return self._status


class DeviceFailureEvent(Event):
    _EVENT_TYPE = EventType.DeviceFailure
    _EVENT_ATTRIBUTE = "device_failure_event"

    def __init__(self, data):
        super().__init__(data)
        self._device = Device(device=data.hDevice)
        self._status = DeviceStatusInfo(data.status)

    @property
    def device(self):
        return self._device

    @property
    def status(self):
        return self._status


class PolicyEvent(Event):
    _EVENT_TYPE = EventType.Policy
    _EVENT_ATTRIBUTE = "policy_event"

    def __init__(self, data):
        super().__init__(data)
        self._flags = data.current_policy

    @property
    def current_policy_flags(self):
        return get_enum_entries(PolicyFlag, self._flags)


class TrackingEvent(Event):
    _EVENT_TYPE = EventType.Tracking
    _EVENT_ATTRIBUTE = "tracking_event"

    def __init__(self, data):
        super().__init__(data)
        self._info = FrameHeader(data.info)
        self._tracking_frame_id = data.tracking_frame_id
        self._num_hands = data.nHands
        self._framerate = data.framerate

        # Copy hands to safe region of memory to protect against use-after-free (UAF)
        self._hands = ffi.new("LEAP_HAND[2]")
        ffi.memmove(self._hands, data.pHands, ffi.sizeof("LEAP_HAND") * data.nHands)

    @property
    def info(self):
        return self._info

    @property
    def timestamp(self):
        return self._info.timestamp

    @property
    def tracking_frame_id(self):
        return self._tracking_frame_id

    @property
    def hands(self):
        return [Hand(self._hands[i]) for i in range(self._num_hands)]

    @property
    def framerate(self):
        return self._framerate


class ImageRequestErrorEvent(Event):
    _EVENT_TYPE = EventType.ImageRequestError
    _EVENT_ATTRIBUTE = "pointer"


class ImageCompleteEvent(Event):
    _EVENT_TYPE = EventType.ImageComplete
    _EVENT_ATTRIBUTE = "pointer"


class LogEvent(Event):
    _EVENT_TYPE = EventType.LogEvent
    _EVENT_ATTRIBUTE = "log_event"


class DeviceLostEvent(Event):
    _EVENT_TYPE = EventType.DeviceLost
    _EVENT_ATTRIBUTE = "device_event"

    def __init__(self, data):
        super().__init__(data)
        self._device = Device(data.device)
        self._status = DeviceStatusInfo(data.status)

    @property
    def device(self):
        return self._device

    @property
    def status(self):
        return self._status


class ConfigResponseEvent(Event):
    _EVENT_TYPE = EventType.ConfigResponse
    _EVENT_ATTRIBUTE = "config_response_event"


class ConfigChangeEvent(Event):
    _EVENT_TYPE = EventType.ConfigChange
    _EVENT_ATTRIBUTE = "config_change_event"


class DeviceStatusChangeEvent(Event):
    _EVENT_TYPE = EventType.DeviceStatusChange
    _EVENT_ATTRIBUTE = "device_status_change_event"

    def __init__(self, data):
        super().__init__(data)
        self._device = Device(data.device)
        self._last_status = DeviceStatusInfo(data.last_status)
        self._status = DeviceStatusInfo(data.status)

    @property
    def device(self):
        return self._device

    @property
    def last_status(self):
        return self._last_status

    @property
    def status(self):
        return self._status


class DroppedFrameEvent(Event):
    _EVENT_TYPE = EventType.DroppedFrame
    _EVENT_ATTRIBUTE = "dropped_frame_event"


class ImageEvent(Event):
    _EVENT_TYPE = EventType.Image
    _EVENT_ATTRIBUTE = "image_event"

    def __init__(self, data):
        super().__init__(data)
        self._images = data.image

    @property
    def image(self):
        return [Image(self._images[0]), Image(self._images[1])]


class PointMappingChangeEvent(Event):
    _EVENT_TYPE = EventType.PointMappingChange
    _EVENT_ATTRIBUTE = "point_mapping_change_event"


class TrackingModeEvent(Event):
    _EVENT_TYPE = EventType.TrackingMode
    _EVENT_ATTRIBUTE = "tracking_mode_event"

    def __init__(self, data):
        super().__init__(data)
        self._tracking_mode = TrackingMode(data.current_tracking_mode)

    @property
    def current_tracking_mode(self):
        return self._tracking_mode


class LogEvents(Event):
    _EVENT_TYPE = EventType.LogEvents
    _EVENT_ATTRIBUTE = "log_events"


class HeadPoseEvent(Event):
    _EVENT_TYPE = EventType.HeadPose
    _EVENT_ATTRIBUTE = "head_pose_event"


class EyesEvent(Event):
    _EVENT_TYPE = EventType.Eyes
    _EVENT_ATTRIBUTE = "eye_event"


class IMUEvent(Event):
    _EVENT_TYPE = EventType.IMU
    _EVENT_ATTRIBUTE = "imu_event"

    def __init__(self, data):
        super().__init__(data)
        self._timestamp = data.timestamp
        self._timestamp_hardware = data.timestamp_hw
        self._flags = data.flags
        self._accelerometer = data.accelerometer
        self._gyroscope = data.gyroscope
        self._temperature = data.temperature

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def timestamp_hardware(self):
        return self._timestamp_hardware

    @property
    def flags(self):
        return get_enum_entries(IMUFlag, self._flags)

    @property
    def acceleration(self):
        return Vector(self._accelerometer)

    @property
    def angular_velocity(self):
        return Vector(self._gyroscope)

    @property
    def temperature(self):
        return self._temperature


def create_event(data):
    """Create an Event from `LEAP_CONNECTION_MESSAGE*` cdata"""
    events = {
        EventType.EventTypeNone: NoneEvent,
        EventType.Connection: ConnectionEvent,
        EventType.ConnectionLost: ConnectionLostEvent,
        EventType.Device: DeviceEvent,
        EventType.DeviceFailure: DeviceFailureEvent,
        EventType.Policy: PolicyEvent,
        EventType.Tracking: TrackingEvent,
        EventType.ImageRequestError: ImageRequestErrorEvent,
        EventType.ImageComplete: ImageCompleteEvent,
        EventType.LogEvent: LogEvent,
        EventType.DeviceLost: DeviceLostEvent,
        EventType.ConfigResponse: ConfigResponseEvent,
        EventType.ConfigChange: ConfigChangeEvent,
        EventType.DeviceStatusChange: DeviceStatusChangeEvent,
        EventType.DroppedFrame: DroppedFrameEvent,
        EventType.Image: ImageEvent,
        EventType.PointMappingChange: PointMappingChangeEvent,
        EventType.TrackingMode: TrackingModeEvent,
        EventType.LogEvents: LogEvents,
        EventType.HeadPose: HeadPoseEvent,
        EventType.Eyes: EyesEvent,
        EventType.IMU: IMUEvent,
    }
    return events[EventType(data.type)].from_connection_message(data)
