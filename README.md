Gemini LeapC Python Bindings
============================

Open-source Python bindings to the Gemini LeapC API. Including build instructions and some simple 
examples. It does not include a pre-compiled python module; the bindings will have to be built 
from source with Gemini already installed.

The latest version of Gemini Hand Tracking can be found here:

https://www.ultraleap.com/tracking/gemini-hand-tracking-platform/


Custom Install
--------------

The module assumes that you have the Leap SDK installed in the default location. If this is not
the case for you, you can use an environment variable to define the installation location. Define
`LEAPSDK_INSTALL_LOCATION` to the path of the `LeapSDK` folder if you have installed to a custom 
location.

Example:
`export LEAP_SDK_INSTALL_LOCATION="C:\Program Files\CustomDir\Ultraleap\LeapSDK"`

By default, this path is the following for each operating system:

- Windows: `C:\Program Files\Ultraleap\LeapSDK`
- MacOS: `/Library/Application Support/Ultraleap/LeapSDK`
- Linux: `TODO`

How to install:
---------------

1. `git clone [insert link here]`
2. Create and activate a virtual environment
3. `pip install -r requirements.txt`
4. `python -m build`
5. `pip install dist/leap-0.0.1.tar.gz`
6. `python examples/image_sample.py`

