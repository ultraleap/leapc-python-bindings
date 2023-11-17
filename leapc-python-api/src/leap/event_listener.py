from typing import Optional

from .events import Event
from .enums import EventType
from .exceptions import LeapError


class Listener:
    """Base class for custom Listeners to Connections

    This should be subclassed and methods overridden to handle events and errors.
    """

    def on_event(self, event: Event):
        """Called every event

        Note that if this method is overridden, the more specific event functions will not be called
        unless the overridden method calls this method.
        """
        getattr(self, self._EVENT_CALLS[event.type])(event)

    def on_error(self, error: LeapError):
        """If an error occurs in polling, the Exception is passed to this function"""
        pass

    def on_none_event(self, event: Event):
        pass

    def on_connection_event(self, event: Event):
        pass

    def on_connection_lost_event(self, event: Event):
        pass

    def on_device_event(self, event: Event):
        pass

    def on_device_failure_event(self, event: Event):
        pass

    def on_policy_event(self, event: Event):
        pass

    def on_tracking_event(self, event: Event):
        pass

    def on_image_request_error_event(self, event: Event):
        pass

    def on_image_complete_event(self, event: Event):
        pass

    def on_log_event(self, event: Event):
        pass

    def on_device_lost_event(self, event: Event):
        pass

    def on_config_response_event(self, event: Event):
        pass

    def on_config_change_event(self, event: Event):
        pass

    def on_device_status_change_event(self, event: Event):
        pass

    def on_dropped_frame_event(self, event: Event):
        pass

    def on_image_event(self, event: Event):
        pass

    def on_point_mapping_change_event(self, event: Event):
        pass

    def on_tracking_mode_event(self, event: Event):
        pass

    def on_log_events(self, event: Event):
        pass

    def on_head_pose_event(self, event: Event):
        pass

    def on_eyes_event(self, event: Event):
        pass

    def on_imu_event(self, event: Event):
        pass

    _EVENT_CALLS = {
        EventType.EventTypeNone: "on_none_event",
        EventType.Connection: "on_connection_event",
        EventType.ConnectionLost: "on_connection_lost_event",
        EventType.Device: "on_device_event",
        EventType.DeviceFailure: "on_device_failure_event",
        EventType.Policy: "on_policy_event",
        EventType.Tracking: "on_tracking_event",
        EventType.ImageRequestError: "on_image_request_error_event",
        EventType.ImageComplete: "on_image_complete_event",
        EventType.LogEvent: "on_log_event",
        EventType.DeviceLost: "on_device_lost_event",
        EventType.ConfigResponse: "on_config_response_event",
        EventType.ConfigChange: "on_config_change_event",
        EventType.DeviceStatusChange: "on_device_status_change_event",
        EventType.DroppedFrame: "on_dropped_frame_event",
        EventType.Image: "on_image_event",
        EventType.PointMappingChange: "on_point_mapping_change_event",
        EventType.TrackingMode: "on_tracking_mode_event",
        EventType.LogEvents: "on_log_events",
        EventType.HeadPose: "on_head_pose_event",
        EventType.Eyes: "on_eyes_event",
        EventType.IMU: "on_imu_event",
    }


class LatestEventListener(Listener):
    def __init__(self, target: EventType):
        self._target = target
        self.event: Optional[Event] = None

    def on_event(self, event: Event):
        if event.type == self._target:
            self.event = event
