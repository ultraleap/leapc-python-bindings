Gemini LeapC Python Bindings
============================

Open-source Python bindings to the Gemini LeapC API. Including build instructions and some simple 
examples to get started with. We include some pre-compiled python objects with our Gemini installation from
5.17 onwards. To use these bindings you will require an installation of Gemini Hand Tracking.

The latest version of Gemini Hand Tracking can be found here:

https://www.ultraleap.com/tracking/gemini-hand-tracking-platform/


Install Instructions:
---------------------

```
# Create and activate a virtual environment
pip install -r requirements.txt
pip install -e leapc-python-api
python examples/tracking_event_example.py
```

Custom Install
--------------

This module assumes that you have the Leap SDK installed in the default location. If this is not the case
for you, you can use an environment variable for define the installation location. Define the environment variable
`LEAPSDK_INSTALL_LOCATION` to the path of the `LeapSDK` folder, if you have installed to a custom location or moved it 
somewhere else.

Example:
`export LEAPSDK_INSTALL_LOCATION="C:\Program Files\CustomDir\Ultraleap\LeapSDK"`

By default, this path is the following for each operating system:
- Windows: `C:/Program Files/Ultraleap/LeapSDK`
- Linux: `/usr/lib/ultraleap-hand-tracking-service`
- Darwin: `/Applications/Ultraleap Hand Tracking.app/Contents/LeapSDK`


Missing Compiled Module?
------------------------

You might not have the correct matching compiled leapc_cffi module for your system, this can cause issues when importing
leap, such as: `ModuleNotFoundError: No module named 'leapc_cffi._leapc_cffi'`
If you'd like to build your own compiled module, you will still require a Gemini install and a C compiler of your 
choice. Follow the steps below:

```
# Create and activate a virtual environment
pip install -r requirements.txt
python -m build leapc-cffi
pip install leapc-cffi/dist/leapc_cffi-0.0.1.tar.gz
pip install leapc-python-api
python examples/tracking_event_example.py
```
