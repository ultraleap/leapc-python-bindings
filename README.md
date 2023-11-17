<!--links-->
[apache]: http://www.apache.org/licenses/LICENSE-2.0 "Apache V2 License"

[developer-site-tracking-software]: https://developer.leapmotion.com/tracking-software-download "Ultraleap Tracking Software"
[developer-site-setup-camera]: https://developer.leapmotion.com/setup-camera "Ultraleap Setup Camera"
[developer-forum]: https://forums.leapmotion.com/ "Developer Forum"
[discord]: https://discord.com/invite/3VCndThqxS "Discord Server"
[github-discussions]: https://github.com/ultraleap/leapc-python-bindings/discussions "Github Discussions"

<!--content-->
# Gemini LeapC Python Bindings

[![mail](https://img.shields.io/badge/Contact-support%40ultraleap.com-00cf75)](mailto:support@ultraleap.com)
[![discord](https://img.shields.io/badge/Discord-Server-blueviolet)][discord]
![GitHub](https://img.shields.io/github/license/ultraleap/leapc-python-bindings)

Open-source Python bindings for the Gemini LeapC API. Allowing developers to use Ultraleaps Hand Tracking technology
with Python. Including build instructions and some simple examples to get started with. 

## Getting Started:

To use this plugin you will need the following:

1. The latest Gemini Ultraleap Hand Tracking Software. You can get this [here][developer-site-tracking-software].
2. An Ultraleap Hand Tracking Camera - follow setup process [here][developer-site-setup-camera].
3. Follow one of the Installation workflows listed below.

## Installation:

This module makes use of a compiled module called `leapc_cffi`. We include some pre-compiled python objects with our
Gemini installation from 5.17 onwards. Supported versions can be found [here](#pre-compiled-module-support). If you 
have the matching python version and have installed Gemini into the default location you can follow the steps below:

```
# Create and activate a virtual environment
pip install -r requirements.txt
pip install -e leapc-python-api
python examples/tracking_event_example.py
```

### Custom Install

This module assumes that you have the Leap SDK installed in the default location. If this is not the case
for you, you can use an environment variable to define the installation location. Define the environment variable
`LEAPSDK_INSTALL_LOCATION` to the path of the `LeapSDK` folder, if you have installed to a custom location or moved it 
somewhere else.

Example:
`export LEAPSDK_INSTALL_LOCATION="C:\Program Files\CustomDir\Ultraleap\LeapSDK"`

By default, this path is the following for each operating system:
- Windows: `C:/Program Files/Ultraleap/LeapSDK`
- Linux x64: `/usr/lib/ultraleap-hand-tracking-service`
- Linux ARM: `/opt/ultraleap/LeapSDK`
- Darwin: `/Applications/Ultraleap Hand Tracking.app/Contents/LeapSDK`

## Pre-Compiled Module Support

The included pre-compiled modules within our 5.17 release currently only support the following versions of python:

- Windows: Python 3.8
- Linux x64: Python 3.8
- Darwin: Python 3.8
- Linux ARM: Python 3.8, 3.9, 3.10, 3.11

Expanded pre-compiled support will be added soon. However, this does not restrict you to these versions, if you wish to 
use a different python version please follow the instructions below to compile your own module.

### Missing Compiled Module?

You might not have the correct matching compiled `leapc_cffi` module for your system, this can cause issues when importing
leap, such as: `ModuleNotFoundError: No module named 'leapc_cffi._leapc_cffi'`
If you'd like to build your own compiled module, you will still require a Gemini install and a C compiler of your 
choice. Follow the steps below:

```
# Create and activate a virtual environment
pip install -r requirements.txt
python -m build leapc-cffi
pip install leapc-cffi/dist/leapc_cffi-0.0.1.tar.gz
pip install -e leapc-python-api
python examples/tracking_event_example.py
```

## Contributing

Our vision is to make it as easy as possible to design the best user experience for hand tracking. 
We learn and are inspired by the creations from our open source community - any contributions you make are 
greatly appreciated.

1. Fork the Project
2. Create your Feature Branch:  
   git checkout -b feature/AmazingFeature
3. Commit your Changes:  
   git commit -m "Add some AmazingFeature"
4. Push to the Branch:  
   git push origin feature/AmazingFeature
5. Open a Pull Request

## License

Use of the LeapC Python Bindings is subject to the [Apache V2 License Agreement][apache].

## Community Support

Our [Discord Server][discord], [Github Discussions][github-discussions] and [Developer Forum][developer-forum] are 
places where you are actively encouraged to share your questions, insights, ideas, feature requests and projects.
