import os
import setuptools
import platform
import shutil

_HERE = os.path.abspath(os.path.dirname(__file__))


def get_system():
    if platform.system() == "Linux" and platform.machine() == "aarch64":
        return "Linux-ARM"
    else:
        return platform.system()


with open(os.path.join(_HERE, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

# The resource directory needs to contain the LeapC headers and libraries
_RESOURCE_DIRECTORY = os.path.join(_HERE, "src/leapc_cffi")

_OS_DEFAULT_HEADER_INSTALL_LOCATION = {
    "Windows": "C:/Program Files/Ultraleap/LeapSDK",
    "Linux": "/usr/include",
    "Linux-ARM": "/opt/ultraleap/LeapSDK",
    "Darwin": "/Applications/Ultraleap Hand Tracking.app/Contents/LeapSDK",
}

_OS_DEFAULT_LIB_INSTALL_LOCATION = {
    "Windows": _OS_DEFAULT_HEADER_INSTALL_LOCATION[get_system()],
    "Linux": "/usr/lib/ultraleap-hand-tracking-service",
    "Linux-ARM": _OS_DEFAULT_HEADER_INSTALL_LOCATION[get_system()],
    "Darwin": _OS_DEFAULT_HEADER_INSTALL_LOCATION[get_system()],
}

_OS_SHARED_OBJECT = {
    "Windows": "LeapC.dll",
    "Linux": "libLeapC.so",
    "Linux-ARM": "libLeapC.so",
    "Darwin": "libLeapC.5.dylib",
}


def setup_symlink(file_path, destination_path):
    if os.path.islink(destination_path):
        os.unlink(destination_path)

    if os.path.exists(destination_path):
        os.remove(destination_path)

    if os.path.exists(file_path):
        try:
            if get_system() != "Windows":
                os.symlink(file_path, destination_path)
            else:
                # Just copy it for windows, so we don't need administrator privileges
                shutil.copy(file_path, destination_path)
        except OSError as error:
            print(error)
            error_msg = (
                "Error "
                + ("creating symlink to " if get_system() != "Windows" else "copying file ")
                + file_path
                + "."
            )
            raise Exception(error_msg)
    else:
        print("Looking for LeapC library at: " + file_path)
        raise Exception(
            "No " + str(_OS_SHARED_OBJECT[get_system()]) + " found, please ensure you "
            "have Ultraleap Gemini Hand Tracking installed, or define LEAPSDK_INSTALL_LOCATION environment "
            "variable to point to a LeapSDK directory."
        )


def gather_leap_sdk():
    _USER_DEFINED_INSTALL_LOCATION = os.getenv("LEAPSDK_INSTALL_LOCATION")
    _OVERRIDE_HEADER_LOCATION = os.getenv("LEAPC_HEADER_OVERRIDE")
    _OVERRIDE_LIB_LOCATION = os.getenv("LEAPC_LIB_OVERRIDE")

    if _USER_DEFINED_INSTALL_LOCATION is not None:
        if get_system() == "Linux":
            print(
                "Warning: The LeapSDK directory with everything in doesn't currently exist on linux. Consider using "
                "LEAPC_HEADER_OVERRIDE and LEAPC_LIB_OVERRIDE environment variables to point to required files."
            )

        print(
            "User defined install location given, using: "
            + str(_USER_DEFINED_INSTALL_LOCATION)
            + " to generate "
            "bindings."
        )
        leapc_header_path = os.path.join(
            _USER_DEFINED_INSTALL_LOCATION,
            "include" if get_system() != "Linux" else "",
            "LeapC.h",
        )
        libleapc_path = os.path.join(
            _USER_DEFINED_INSTALL_LOCATION,
            "lib" if get_system() != "Linux" else "",
            "x64" if get_system() == "Windows" else "",
            _OS_SHARED_OBJECT[get_system()],
        )
    else:
        leapc_header_path = os.path.join(
            _OS_DEFAULT_HEADER_INSTALL_LOCATION[get_system()],
            "include" if get_system() != "Linux" else "",
            "LeapC.h",
        )
        libleapc_path = os.path.join(
            _OS_DEFAULT_LIB_INSTALL_LOCATION[get_system()],
            "lib" if get_system() != "Linux" else "",
            "x64" if get_system() == "Windows" else "",
            _OS_SHARED_OBJECT[get_system()],
        )

    # Override
    if _OVERRIDE_HEADER_LOCATION is not None:
        print("Header override location given, using: " + str(_OVERRIDE_HEADER_LOCATION))
        leapc_header_path = _OVERRIDE_HEADER_LOCATION

    if _OVERRIDE_LIB_LOCATION is not None:
        print("Library override location given, using: " + str(_OVERRIDE_LIB_LOCATION))
        libleapc_path = _OVERRIDE_LIB_LOCATION

    # Copy the found header
    if os.path.exists(leapc_header_path):
        shutil.copy(leapc_header_path, os.path.join(_RESOURCE_DIRECTORY, "LeapC.h"))
    else:
        raise Exception(
            "No LeapC.h found, please ensure you have Ultraleap Gemini Hand Tracking installed, or define "
            "LEAPSDK_INSTALL_LOCATION environment variable to point to a LeapSDK directory."
        )

    # Create a symlink for the shared object
    symlink_path = os.path.join(_RESOURCE_DIRECTORY, _OS_SHARED_OBJECT[get_system()])
    setup_symlink(libleapc_path, symlink_path)

    # On windows we also need to manage the LeapC.lib file
    if get_system() == "Windows":
        if _USER_DEFINED_INSTALL_LOCATION is not None:
            windows_lib_path = os.path.join(
                _USER_DEFINED_INSTALL_LOCATION, "lib", "x64", "LeapC.lib"
            )
        else:
            windows_lib_path = os.path.join(
                _OS_DEFAULT_LIB_INSTALL_LOCATION[get_system()], "lib", "x64", "LeapC.lib"
            )
        symlink_lib_path = os.path.join(_RESOURCE_DIRECTORY, "LeapC.lib")
        setup_symlink(windows_lib_path, symlink_lib_path)


gather_leap_sdk()

setuptools.setup(
    name="leapc_cffi",
    version="0.0.1",
    author="Ultraleap",
    description="Python CFFI bindings for LeapC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    exclude_package_data={
        "": ["*.h", "*.lib", "scripts/*"]
    },  # Excluded from the installed package
    python_requires=">=3.8",
    setup_requires=["cffi"],
    install_requires=["cffi"],
    ext_package="leapc_cffi",  # The location that the CFFI module will be built
    cffi_modules=["src/scripts/cffi_build.py:ffibuilder"],
)
