from contextlib import contextmanager
import sys
import threading
from typing import Dict, Optional, List, Callable
from timeit import default_timer as timer
import time
import json

from leapc_cffi import ffi, libleapc

from .device import Device
from .enums import (
    ConnectionStatus,
    EventType,
    RS as LeapRS,
    ConnectionConfig as ConnectionConfigEnum,
    TrackingMode,
    PolicyFlag,
)
from .event_listener import LatestEventListener, Listener
from .events import create_event, Event
from .exceptions import (
    create_exception,
    success_or_raise,
    LeapError,
    LeapConnectionAlreadyOpen,
    LeapConcurrentPollError,
    LeapNotConnectedError,
    LeapTimeoutError,
)


class ConnectionConfig:
    """Configuration for a Connection

    Allows a user to enable multi device functionality prior to connection.
    """

    def __init__(
        self,
        *,
        server_namespace: Optional[Dict[str, str]] = None,
        multi_device_aware: bool = False,
    ):
        self._data_ptr = ffi.new("LEAP_CONNECTION_CONFIG*")
        self._data_ptr.server_namespace = server_namespace
        self._data_ptr.flags = 0
        self._data_ptr.size = ffi.sizeof(self._data_ptr[0])

        if multi_device_aware:
            self._data_ptr.flags |= ConnectionConfigEnum.MultiDeviceAware.value


class Connection:
    """Connection to a Leap Server

    :param listeners: A List of event listeners. Defaults to None
    :param poll_timeout: A timeout of poll messages, in seconds. Defaults to 1 second.
    :param response_timeout: A timeout to wait for specific events in response to events.
        Defaults to 10 seconds.
    """

    def __init__(
        self,
        *,
        server_namespace: Optional[Dict[str, str]] = None,
        multi_device_aware: bool = False,
        listeners: Optional[List[Listener]] = None,
        poll_timeout: float = 1,
        response_timeout: float = 10,
    ):
        if listeners is None:
            listeners = []
        self._listeners = listeners

        self._connection_ptr = self._create_connection(server_namespace, multi_device_aware)

        self._poll_timeout = int(poll_timeout * 1000)  # Seconds to milliseconds
        self._response_timeout = int(response_timeout)
        self._stop_poll_flag = False

        self._is_open = False
        self._poll_thread = None

    def __del__(self):
        # Since 'destroy_connection' only tells C to free the memory that it allocated
        # for our connection, it is appropriate to leave the deletion of this to the garbage
        # collector.
        if hasattr(self, "_connection_ptr"):
            # We have this 'if' statement to deal with the possibility that an Exception
            # could be raised in the __init__ method, before this has been assigned.
            self._destroy_connection(self._connection_ptr)

    def add_listener(self, listener: Listener):
        self._listeners.append(listener)

    def remove_listener(self, listener: Listener):
        self._listeners.remove(listener)

    def poll(self, timeout: Optional[float] = None) -> Event:
        """Manually poll the connection from this thread

        Do not notify listeners about the result of this poll.

        :param timeout: The timeout of the poll, in seconds.
            Defaults to the number the Connection was initialised with.
        """
        if self._poll_thread is not None:
            raise LeapConcurrentPollError
        if timeout is None:
            timeout = self._poll_timeout
        else:
            timeout = int(timeout * 1000)  # Seconds to milliseconds
        event_ptr = ffi.new("LEAP_CONNECTION_MESSAGE*")
        success_or_raise(libleapc.LeapPollConnection, self._connection_ptr[0], timeout, event_ptr)
        return create_event(event_ptr)

    def poll_until(
        self,
        event_type: EventType,
        *,
        timeout: Optional[float] = None,
        individual_poll_timeout: Optional[float] = None,
    ) -> Event:
        """Manually poll the connection until a specific event type is received

        Discard all other events. Do not notify listeners about the results of any polls.
        """
        if timeout is None:
            timeout = self._response_timeout
        start_time = timer()
        while timer() - start_time < timeout:
            try:
                event = self.poll(individual_poll_timeout)
                if isinstance(event, event_type):
                    return event
            except LeapTimeoutError:
                pass
        raise LeapTimeoutError

    def wait_for(self, event_type: EventType, *, timeout: Optional[float] = None) -> Event:
        """Wait until the specified event type is emitted

        Returns the next event of the requested type.
        """
        if not self._is_open:
            raise LeapNotConnectedError

        return self._call_and_wait_for_event(event_type, func=None, timeout=timeout)

    @contextmanager
    def open(self, *, auto_poll: bool = True, timeout: float = 10):
        """Open the Connection

        Optionally starts a separate thread which continually polls the connection.

        :param auto_poll: Whether to launch a separate thread to poll the connection.
            Defaults to True.
        :param timeout: A timeout for initial connection in seconds. This may be greater than
            the usual poll timeout. Defaults to 10s.
        """
        self.connect(auto_poll=auto_poll, timeout=timeout)
        try:
            yield self
        finally:
            self.disconnect()

    def connect(self, *, auto_poll: bool = True, timeout: float = 10):
        """Open the connection

        The caller is responsible for disconnecting afterwards.

        Optionally starts a separate thread which continually polls the connection.

        :param auto_poll: Whether to launch a separate thread to poll the connection.
            Defaults to True.
        :param timeout: A timeout for initial connection in seconds. This may be greater than
            the usual poll timeout. Defaults to 10s.
        """
        if self._is_open:
            raise LeapConnectionAlreadyOpen

        self._open_connection()

        if auto_poll:
            self._start_poll_thread(timeout)

    def disconnect(self):
        self._stop_poll_thread()
        self._close_connection()

    def set_tracking_mode(self, mode: TrackingMode):
        """Set the Server tracking mode"""
        success_or_raise(libleapc.LeapSetTrackingMode, self._connection_ptr[0], mode.value)

    def get_tracking_mode(self) -> TrackingMode:
        """Get the Server tracking mode"""
        func = success_or_raise
        args = (libleapc.LeapGetTrackingMode, self._connection_ptr[0])

        event = self._call_and_wait_for_event(EventType.TrackingMode, func, args)
        return event.current_tracking_mode

    def set_policy_flags(
        self,
        flags_to_set: Optional[List[PolicyFlag]] = None,
        flags_to_clear: Optional[List[PolicyFlag]] = None,
    ) -> List[PolicyFlag]:
        """Set the policy flags

        Returns a list of current policy flags.

        :param flags_to_set: A list of PolicyFlags to set. Defaults to None.
        :param flags_to_clear: A list of PolicyFlags to clear. Defaults to None.
        """
        to_set = 0
        if flags_to_set is not None:
            for flag in flags_to_set:
                to_set |= flag.value

        to_clear = 0
        if flags_to_clear is not None:
            for flag in flags_to_clear:
                to_clear |= flag.value

        func = success_or_raise
        args = (libleapc.LeapSetPolicyFlags, self._connection_ptr[0], to_set, to_clear)
        event = self._call_and_wait_for_event(EventType.Policy, func, args)
        return event.current_policy_flags

    def get_policy_flags(self) -> List[PolicyFlag]:
        """Get the current policy flags"""
        return self.set_policy_flags()

    def get_status(self) -> ConnectionStatus:
        """Get information about the current connection"""
        connection_info_ptr = ffi.new("LEAP_CONNECTION_INFO*")
        size_of_info = ffi.sizeof(connection_info_ptr[0])
        connection_info_ptr.size = size_of_info
        success_or_raise(
            libleapc.LeapGetConnectionInfo, self._connection_ptr[0], connection_info_ptr
        )
        return ConnectionStatus(connection_info_ptr.status)

    def get_devices(self) -> List[Device]:
        """Get the devices which the Server knows about"""
        count_ptr = ffi.new("uint32_t*")
        success_or_raise(libleapc.LeapGetDeviceList, self._connection_ptr[0], ffi.NULL, count_ptr)
        devices_ptr = ffi.new("LEAP_DEVICE_REF[]", count_ptr[0])
        success_or_raise(
            libleapc.LeapGetDeviceList, self._connection_ptr[0], devices_ptr, count_ptr
        )
        return [Device(devices_ptr[i], owner=devices_ptr) for i in range(count_ptr[0])]

    def set_primary_device(self, device: Device, unsubscribe_others: bool = False):
        """Sets the primary device

        :param device: The device to make primary
        :param unsubscribe_others: Whether to unsubscribe other devices
        """
        success_or_raise(
            libleapc.LeapSetPrimaryDevice,
            self._connection_ptr[0],
            device.c_data_device,
            unsubscribe_others,
        )

    def get_connection_ptr(self) -> ffi.CData:
        return self._connection_ptr[0]

    def subscribe_events(self, device: Device):
        """Subscribe to events from the device

        :param device: The device to subscribe to
        """
        success_or_raise(
            libleapc.LeapSubscribeEvents, self._connection_ptr[0], device.c_data_device
        )

    def unsubscribe_events(self, device: Device):
        """Unsubscribe from events from the device

        :param device: The device to unsubscribe from
        """
        success_or_raise(
            libleapc.LeapUnsubscribeEvents,
            self._connection_ptr[0],
            device.c_data_device,
        )

    @staticmethod
    def _create_connection(
        server_namespace: Optional[Dict] = None, multi_device_aware: bool = False
    ) -> ffi.CData:
        connection_ptr = ffi.new("LEAP_CONNECTION*")
        ffi_server_namespace = ffi.new("char []", json.dumps(server_namespace).encode("ascii"))

        config = ConnectionConfig(
            server_namespace=ffi_server_namespace, multi_device_aware=multi_device_aware
        )

        raw_result = libleapc.LeapCreateConnection(config._data_ptr, connection_ptr)
        result = LeapRS(raw_result)
        if result != LeapRS.Success:
            raise create_exception(result, "Unable to create connection")
        return connection_ptr

    @staticmethod
    def _destroy_connection(connection_ptr: ffi.CData):
        # Destroy the connection. Must be done on all created connections.
        libleapc.LeapDestroyConnection(connection_ptr[0])

    def _open_connection(self):
        # Open the connection
        open_result = libleapc.LeapOpenConnection(self._connection_ptr[0])
        if LeapRS(open_result) != LeapRS.Success:
            raise create_exception(LeapRS(open_result), "Unable to open connection")
        self._is_open = True

    def _close_connection(self):
        # Close the connection. Must be done on all opened connections.
        if self._connection_ptr is not None:
            libleapc.LeapCloseConnection(self._connection_ptr[0])
        self._is_open = False

    def _start_poll_thread(self, startup_timeout: float):
        self._poll_thread = threading.Thread(target=self._poll_loop)
        try:
            self._call_and_wait_for_event(
                EventType.Connection, self._poll_thread.start, timeout=startup_timeout
            )
        except LeapTimeoutError as exc:
            self._stop_poll_thread()
            raise exc

    def _stop_poll_thread(self):
        if self._poll_thread is not None:
            self._stop_poll_flag = True
            self._poll_thread.join()
            self._stop_poll_flag = False
            self._poll_thread = None

    def _poll_loop(self):
        event_ptr = ffi.new("LEAP_CONNECTION_MESSAGE*")
        while True:
            if self._stop_poll_flag:
                break
            try:
                success_or_raise(
                    libleapc.LeapPollConnection,
                    self._connection_ptr[0],
                    self._poll_timeout,
                    event_ptr,
                )
                event = create_event(event_ptr)
                for listener in self._listeners:
                    try:
                        listener.on_event(event)
                    except Exception as exc:
                        msg = f"Caught exception in listener callback: {type(exc)}, {exc}, {exc.__traceback__}"
                        print(msg, file=sys.stderr)
            except LeapError as exc:
                for listener in self._listeners:
                    listener.on_error(exc)

    def _call_and_wait_for_event(
        self,
        event_type: EventType,
        func: Optional[Callable] = None,
        args: Optional[tuple] = None,
        *,
        timeout: Optional[float] = None,
    ) -> Event:
        """Wait for an event after an (optional) function call.

        If a function is supplied, it will be called with the specified args. This adds the
        event-listener to the connection before calling, so that the event is guaranteed to
        be found no matter how quickly after calling it is emitted.

        Return the requested event.
        """
        listener = LatestEventListener(event_type)
        self.add_listener(listener)

        if func is not None:
            if args is None:
                args = []

            try:
                func(*args)
            except Exception as exc:
                self.remove_listener(listener)
                raise exc

        if timeout is None:
            timeout = self._response_timeout

        start_time = timer()
        while listener.event is None and timer() - start_time < timeout:
            time.sleep(0.01)
        self.remove_listener(listener)

        if listener.event is None:
            raise LeapTimeoutError("Did not received expected event in time")
        return listener.event
