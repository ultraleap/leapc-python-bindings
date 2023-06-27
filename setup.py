import os
import setuptools
import platform
import shutil

_HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_HERE, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

# The resource directory needs to contain the LeapC headers and libraries
_RESOURCE_DIRECTORY = os.path.join(_HERE, "src/leap/leapc")

_OS_DEFAULT_INSTALL_LOCATION = {
    "Windows": "C:/Program Files/Ultraleap/LeapSDK",
    "Linux": "/usr/share/doc/ultraleap-hand-tracking-service/LeapSDK",
    "Darwin": "/Library/Application Support/Ultraleap/LeapSDK"
}

_OS_SHARED_OBJECT = {
    "Windows": "LeapC.lib",
    "Linux": "so",
    "Darwin": "libLeapC.5.dylib"
}


def os_specific_lib_dir(os_name):
    if os_name == "Windows":
        # On windows the libs are within the x64 directory
        return "x64"
    else:
        # On other OS's it's within the root of lib
        return ""


def gather_leap_sdk():
    _USER_DEFINED_INSTALL_LOCATION = os.getenv('LEAPSDK_INSTALL_LOCATION')
    if _USER_DEFINED_INSTALL_LOCATION is not None:
        print("User defined install location given, using: " + str(_USER_DEFINED_INSTALL_LOCATION) + " to generate "
              "bindings.")
        leapc_header_path = os.path.join(_USER_DEFINED_INSTALL_LOCATION, "include/LeapC.h")
        libleapc_path = os.path.join(_USER_DEFINED_INSTALL_LOCATION, "lib", os_specific_lib_dir(platform.system()), _OS_SHARED_OBJECT[platform.system()])
    else:
        leapc_header_path = os.path.join(_OS_DEFAULT_INSTALL_LOCATION[platform.system()], "include/LeapC.h")
        libleapc_path = os.path.join(_OS_DEFAULT_INSTALL_LOCATION[platform.system()], "lib", os_specific_lib_dir(platform.system()), _OS_SHARED_OBJECT[platform.system()])

    # Copy the found header
    if os.path.exists(leapc_header_path):
        shutil.copy(leapc_header_path, _RESOURCE_DIRECTORY)
    else:
        raise Exception("No LeapC.h found, please ensure you have Ultraleap Gemini Hand Tracking installed, or define "
                        "LEAPSDK_INSTALL_LOCATION environment variable to point to a LeapSDK directory.")

    # Create a symlink for the shared object
    symlink_path = os.path.join(_RESOURCE_DIRECTORY, _OS_SHARED_OBJECT[platform.system()])
    if os.path.islink(symlink_path):
        os.unlink(symlink_path)

    if os.path.exists(symlink_path):
        os.remove(symlink_path)

    if os.path.exists(libleapc_path):
        if platform.system() == "Windows":
            shutil.copyfile(libleapc_path, symlink_path)
        else:
            os.symlink(libleapc_path, symlink_path)
    else:
        print("Looking for libLeapC at: " + libleapc_path)
        raise Exception("No " + str(_OS_SHARED_OBJECT[platform.system()]) + " found, please ensure you "
                        "have Ultraleap Gemini Hand Tracking installed, or define LEAPSDK_INSTALL_LOCATION environment "
                        "variable to point to a LeapSDK directory.")


gather_leap_sdk()

setuptools.setup(
    name="leap",
    version="0.0.1",
    author="Ultraleap",
    description="Python wrappers around LeapC bindings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    exclude_package_data={
        "": ["*.h", "*.lib", "scripts/*"]
    },  # Excluded from the installed package
    python_requires=">=3.6",
    setup_requires=["cffi"],
    install_requires=["cffi", "numpy", "websocket-client"],
    ext_package="leap/leapc",  # The location that the CFFI module will be built
    cffi_modules=["src/leap/scripts/cffi_build.py:ffibuilder"],
)
