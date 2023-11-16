""" Leap Package """
import fnmatch

# Set up some functions we want to be available at the top level

import sys
import platform
import os

_OS_DEFAULT_CFFI_INSTALL_LOCATION = {
    "Windows": "C:/Program Files/Ultraleap/LeapSDK",
    "Linux": "/usr/lib/ultraleap-hand-tracking-service",
    "Linux-ARM": "/opt/ultraleap/LeapSDK",
    "Darwin": "/Applications/Ultraleap Hand Tracking.app/Contents/LeapSDK",
}

_OS_REQUIRED_CFFI_FILES = {
    "Windows": ["__init__.py", "LeapC.lib", "LeapC.dll"],
    "Linux": ["__init__.py", "libLeapC.so", "libLeapC.so.5"],
    "Linux-ARM": ["__init__.py", "libLeapC.so", "libLeapC.so.5"],
    "Darwin": ["__init__.py", "libLeapC.5.dylib", "libLeapC.dylib"],
}

_OS_CFFI_SHARED_OBJECT_PATTERN = {
    "Windows": "_leapc_cffi*.pyd",
    "Linux": "_leapc_cffi*.so",
    "Linux-ARM": "_leapc_cffi*.so",
    "Darwin": "_leapc_cffi*.so",
}


def get_system():
    if platform.system() == "Linux" and platform.machine() == "aarch64":
        return "Linux-ARM"
    else:
        return platform.system()


def check_required_files(cffi_dir):
    directory_files = [
        f for f in os.listdir(cffi_dir) if os.path.isfile(os.path.join(cffi_dir, f))
    ]

    shared_object_files = [
        f
        for f in directory_files
        if fnmatch.fnmatch(f, _OS_CFFI_SHARED_OBJECT_PATTERN[get_system()])
    ]
    if len(shared_object_files) < 1:
        return False

    for file in _OS_REQUIRED_CFFI_FILES[get_system()]:
        if file not in directory_files:
            return False

    return True


_OVERRIDE_LEAPSDK_LOCATION = os.getenv("LEAPSDK_INSTALL_LOCATION")

cffi_location = _OS_DEFAULT_CFFI_INSTALL_LOCATION[get_system()]
if _OVERRIDE_LEAPSDK_LOCATION is not None:
    cffi_location = _OVERRIDE_LEAPSDK_LOCATION

cffi_path = os.path.join(cffi_location, "leapc_cffi")
if os.path.isdir(cffi_path):
    ret = check_required_files(cffi_path)

    # TODO: If we can't find leapc_cffi, we could try building it

    sys.path.append(cffi_location)

    try:
        from leapc_cffi import ffi, libleapc
    except ImportError as import_error:
        if not ret:
            error_msg = f"Missing required files within {cffi_location}."
        else:
            error_msg = f"Unknown error, please consult readme for help. Attempting to find leapc_cffi within {cffi_location}"
        raise ImportError(
            f"Cannot import leapc_cffi: {error_msg}. Caught ImportError: {import_error}"
        )
else:
    error_msg = f"Error: Unable to find leapc_cffi dir within directory {cffi_location}"
    raise Exception(error_msg)

from .functions import (
    get_now,
    get_server_status,
    get_frame_size,
    interpolate_frame,
    get_extrinsic_matrix,
)
from .connection import Connection
from .enums import EventType, TrackingMode, HandType
from .event_listener import Listener
from .exceptions import LeapError
from .recording import Recording, Recorder
