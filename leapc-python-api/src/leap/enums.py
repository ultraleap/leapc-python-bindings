"""Wrappers around LeapC enums"""

import enum
from keyword import iskeyword

from leapc_cffi import libleapc


def _generate_enum_entries(container, name: str):
    """Generate enum entries based on the attributes of the container

    This searches for all attributes which start with "eLeap{name}_".

    It yields a tuple which is the remainder of the attribute name, and
    the corresponding attribute value. If the attribute name is a Python
    keyword then it is prefixed with the "name" input.

    Example:
    ```
    class MyClass:
        eLeapFoo_One = 1
        eLeapFoo_Two = 2
        eLeapBar_Three = 3
        eLeapFoo_None = 4

    list(generate_enum_entries(MyClass, 'Foo'))
    > [('One', 1), ('Two', 2), ('FooNone', 4)]
    ```
    """
    prefix = f"eLeap{name}_"
    for attr in dir(container):
        if attr.startswith(prefix):
            enum_key = attr[len(prefix) :]
            enum_value = getattr(container, attr)
            if iskeyword(enum_key):
                enum_key = f"{name}{enum_key}"
            yield enum_key, enum_value


class LeapEnum(type):
    """Metaclass used to generate Python Enum classes from LeapC enums

    Usage: Defining an empty class with this as its metaclass will create an
    enum.Enum class with the same name. The LeapC API will be searched for an
    enum of a matching name, and all entries will be created in this class.

    Example:
        Suppose the LeapC API has an enum `Foo` defined by:
            `[libleapc.eLeapFoo_One, libleapc.eLeapFoo_Two]`

        If we define a class via
        `class Foo(metaclass=LeapEnum): pass`
        Then a class will be generated which is equivalent to
        ```
        class Foo(enum.Enum):
            One = libleapc.eLeapFoo_One
            Two = libleapc.eLeapFoo_Two
        ```

    If an enum name is a Python keyword, it will be prefixed with the class
    name. Eg, instead of generating `Foo.None` it will generate `Foo.FooNone`.
    """

    _LIBLEAPC = libleapc

    def __new__(cls, name, bases, dct):
        entries = _generate_enum_entries(cls._LIBLEAPC, name)
        return enum.Enum(name, entries)


def get_enum_entries(enum_type, flags):
    """Interpret the flags as a bitwise combination of enum values

    Returns a list of enum entries which are present in the 'flags'.
    """
    return list(filter(lambda entry: entry.value & flags != 0, enum_type))


class RS(metaclass=LeapEnum):
    pass


class TrackingMode(metaclass=LeapEnum):
    pass


class ConnectionConfig(metaclass=LeapEnum):
    pass


class AllocatorType(metaclass=LeapEnum):
    pass


class ServiceDisposition(metaclass=LeapEnum):
    pass


class ConnectionStatus(metaclass=LeapEnum):
    pass


class PolicyFlag(metaclass=LeapEnum):
    pass


class ValueType(metaclass=LeapEnum):
    pass


class DevicePID(metaclass=LeapEnum):
    pass


class DeviceStatus(metaclass=LeapEnum):
    pass


class ImageType(metaclass=LeapEnum):
    pass


class ImageFormat(metaclass=LeapEnum):
    pass


class PerspectiveType(metaclass=LeapEnum):
    pass


class CameraCalibrationType(metaclass=LeapEnum):
    pass


class HandType(metaclass=LeapEnum):
    pass


class LogSeverity(metaclass=LeapEnum):
    pass


class DroppedFrameType(metaclass=LeapEnum):
    pass


class IMUFlag(metaclass=LeapEnum):
    pass


class EventType(metaclass=LeapEnum):
    pass


class RecordingFlags(metaclass=LeapEnum):
    pass


class VersionPart(metaclass=LeapEnum):
    pass
