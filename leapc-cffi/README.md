CFFI Python Binds For LeapC
===========================

Low-level Python bindings for LeapC. These bindings are used by the leap module to interface with the LeapC API.

A built shared object of this is included in the Gemini Hand Tracking install from v5.17 onwards. However, you can 
manually build this if it does not include a shared object for your python version or architecture. 

Below are the instructions on how to compile manually (requiring a C compiler):

```
# Create and activate a virtual environment
pip install -r requirements.txt
python -m build leapc-cffi
pip install leapc-cffi/dist/leapc_cffi-0.0.1.tar.gz
pip install -e leapc-python-api
python examples/tracking_event_example.py
```

Building Errors
---------------

This will try to use the LeapC shared object from your install of Gemini Hand Tracking. This module assumes that you 
have the Leap SDK installed in the default location. If this is not the case for you, you can use an environment 
variable to define the installation location. Define the environment variable `LEAPSDK_INSTALL_LOCATION` to the path of
the `LeapSDK` folder, if you have installed to a custom location or moved it somewhere else.

Example:
`export LEAPSDK_INSTALL_LOCATION="C:\Program Files\CustomDir\Ultraleap\LeapSDK"`

By default, this path is the following for each operating system:
- Windows: `C:/Program Files/Ultraleap/LeapSDK`
- Linux x64: `/usr/lib/ultraleap-hand-tracking-service`
- Linux ARM: `/opt/ultraleap/LeapSDK`
- Darwin: `/Applications/Ultraleap Hand Tracking.app/Contents/LeapSDK`
