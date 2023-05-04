"""Wrap around LeapC functions"""

from .exceptions import success_or_raise
from .leapc import ffi, libleapc


def get_now():
    """Get the current time"""
    return libleapc.LeapGetNow()


def get_server_status(timeout):
    server_status_pp = ffi.new("LEAP_SERVER_STATUS**")
    success_or_raise(libleapc.LeapGetServerStatus, timeout, server_status_pp)

    try:
        result = {
            "version": ffi.string(server_status_pp[0].version).decode("utf-8"),
            "devices": [],
        }

        for i in range(server_status_pp[0].device_count):
            result["devices"].append(
                {
                    "serial": ffi.string(server_status_pp[0].devices[i].serial).decode("utf-8"),
                    "type": ffi.string(server_status_pp[0].devices[i].type).decode("utf-8"),
                }
            )

    finally:
        libleapc.LeapReleaseServerStatus(server_status_pp[0])

    return result


def get_frame_size(connection, target_frame_time, target_frame_size):
    # target_frame_size = ffi.new("uint64_t*")

    success_or_raise(
        libleapc.LeapGetFrameSize,
        connection.get_connection_ptr(),
        target_frame_time[0],
        target_frame_size,
    )


def interpolate_frame(connection, target_frame_time, buffer, frame_size):
    frame_ptr = ffi.cast("LEAP_TRACKING_EVENT*", buffer)

    success_or_raise(
        libleapc.LeapInterpolateFrame,
        connection.get_connection_ptr(),
        target_frame_time,
        frame_ptr,
        frame_size,
    )


def get_extrinsic_matrix(connection, camera):
    matrix = ffi.new("float[]", 16)
    libleapc.LeapExtrinsicCameraMatrix(connection.get_connection_ptr(), camera.value, matrix)
    return matrix
