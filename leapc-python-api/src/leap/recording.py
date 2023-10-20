from leapc_cffi import libleapc, ffi

from .enums import RecordingFlags
from .event_listener import Listener
from .events import TrackingEvent
from .exceptions import success_or_raise, LeapUnknownError


class Recording:
    def __init__(self, fpath, mode="r"):
        self._fpath = ffi.new("char[]", fpath.encode("utf-8"))
        self._recording_ptr = ffi.new("LEAP_RECORDING*")
        self._recording_params_ptr = ffi.new("LEAP_RECORDING_PARAMETERS*")
        self._recording_params_ptr.mode = self._parse_mode(mode)
        self._read_buffer = ffi.new("uint8_t*", 0)

    def __enter__(self):
        success_or_raise(
            libleapc.LeapRecordingOpen,
            self._recording_ptr,
            self._fpath,
            self._recording_params_ptr[0],
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        success_or_raise(libleapc.LeapRecordingClose, self._recording_ptr)

    def write(self, frame):
        """Write a frame of tracking data to the recording"""
        bytes_written = ffi.new("uint64_t*")
        success_or_raise(
            libleapc.LeapRecordingWrite,
            self._recording_ptr[0],
            frame._data,
            bytes_written,
        )

    def __iter__(self):
        return self

    def __next__(self):
        return self.read_frame()

    def read(self):
        """Read the recording

        Returns a list of TrackingEvents in the recording.
        """
        return list(self)

    def read_frame(self):
        frame_size = ffi.new("uint64_t*")
        try:
            success_or_raise(libleapc.LeapRecordingReadSize, self._recording_ptr[0], frame_size)
        except LeapUnknownError:
            # When the recording has finished reading, an "UnknownError" is
            # returned from the LeapC API.
            raise StopIteration

        frame_data = self._FrameData(frame_size[0])

        success_or_raise(
            libleapc.LeapRecordingRead,
            self._recording_ptr[0],
            frame_data.buffer_ptr(),
            frame_size[0],
        )
        return TrackingEvent(frame_data)

    def status(self):
        """Get the current recording status

        Return a string, which may contain or omit the following characters:
            'rwfc'
                'r': Reading
                'w': Writing
                'f': Flushing
                'c': Compressed

        Raises a RuntimeError if the recording is an invalid state.
        """
        recording_status = ffi.new("LEAP_RECORDING_STATUS*")
        success_or_raise(libleapc.LeapRecordingGetStatus, self._recording_ptr[0], recording_status)

        flags = recording_status.mode
        mode = ""

        if flags & RecordingFlags.Reading.value:
            mode += "r"
        if flags & RecordingFlags.Writing.value:
            mode += "w"
        if flags & RecordingFlags.Flushing.value:
            mode += "f"
        if flags & RecordingFlags.Compressed.value:
            mode += "c"

        if len(mode) == 0:
            raise RuntimeError("Recording is in an invalid state")
        return mode

    @staticmethod
    def _parse_mode(mode):
        flags = RecordingFlags.Error.value
        if "r" in mode:
            flags |= RecordingFlags.Reading.value
        if "w" in mode:
            flags |= RecordingFlags.Writing.value
        if "c" in mode:
            flags |= RecordingFlags.Compressed.value
        return flags

    class _FrameData:
        """Wrapper which owns all the data required to read the Frame

        A LEAP_TRACKING_EVENT has a fixed size, but some fields are pointers to memory stored
        outside of the struct. This means the size required for all the information about a
        frame is larger than the size of the struct.

        This wrapper owns the buffer required for all of that data. Reading attributes or
        items from this wrapper returns the corresponding item or wrapper on the underlying
        LEAP_TRACKING_EVENT.

        It is intended to by used in the TrackingEvent constructor.
        """

        def __init__(self, size):
            self._buffer = ffi.new("char[]", size)
            self._frame_ptr = ffi.cast("LEAP_TRACKING_EVENT*", self._buffer)

        def __getattr__(self, name):
            return getattr(self._frame_ptr, name)

        def __getitem__(self, key):
            return self._frame_ptr[key]

        def buffer_ptr(self):
            return self._frame_ptr


class Recorder(Listener):
    def __init__(self, recording, *, auto_start=True):
        self._recording = recording
        self._running = auto_start

    def on_tracking_event(self, event):
        if self._running:
            self._recording.write(event)

    def start(self):
        self._running = True

    def stop(self):
        self._running = False
