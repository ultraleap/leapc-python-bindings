"""Wrap around LeapC functions"""
import leap.enums

from .enums import PerspectiveType
from .connection import Connection
from .exceptions import success_or_raise
from leapc_cffi import ffi, libleapc

from typing import Optional, List, Dict


def get_now() -> int:
    """Get the current time"""
    return libleapc.LeapGetNow()


def get_server_status(timeout: float) -> Dict[str, Optional[List[Dict[str, str]]]]:
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


def get_frame_size(
    connection: Connection, target_frame_time: ffi.CData, target_frame_size: ffi.CData
) -> None:
    success_or_raise(
        libleapc.LeapGetFrameSize,
        connection.get_connection_ptr(),
        target_frame_time[0],
        target_frame_size,
    )


def interpolate_frame(
    connection: Connection,
    target_frame_time: ffi.CData,
    frame_ptr: ffi.CData,
    frame_size: ffi.CData,
) -> None:
    success_or_raise(
        libleapc.LeapInterpolateFrame,
        connection.get_connection_ptr(),
        target_frame_time,
        frame_ptr,
        frame_size,
    )


def get_extrinsic_matrix(connection: Connection, camera: PerspectiveType) -> ffi.CData:
    matrix = ffi.new("float[]", 16)
    libleapc.LeapExtrinsicCameraMatrix(connection.get_connection_ptr(), camera.value, matrix)
    return matrix
