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
    "Windows": "Program Files..",
    "Linux": "Somewhere",
    "Darwin": "/Library/Application Support/Ultraleap/LeapSDK"
}

_OS_SHARED_OBJECT_EXT = {
    "Windows": "dll",
    "Linux": "so",
    "Darwin": "dylib"
}


def setup_files():
    # TODO: Also do something special if environment variable was provided

    leapc_header_path = os.path.join(_OS_DEFAULT_INSTALL_LOCATION[platform.system()], "include/LeapC.h")
    shutil.copy(leapc_header_path, _RESOURCE_DIRECTORY)

    # Can't use symlink but we could copy the shared object
    libleapc_path = os.path.join(_OS_DEFAULT_INSTALL_LOCATION[platform.system()], "lib/libLeapC." + _OS_SHARED_OBJECT_EXT[platform.system()])
    symlink_path = os.path.join(_RESOURCE_DIRECTORY, "libLeapC.5." + _OS_SHARED_OBJECT_EXT[platform.system()])

    if os.path.islink(symlink_path):
        os.unlink(symlink_path)

    if os.path.exists(symlink_path):
        os.remove(symlink_path)

    os.symlink(libleapc_path, symlink_path)


setup_files()

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