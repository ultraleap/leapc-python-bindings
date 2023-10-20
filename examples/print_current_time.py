"""
This is a simple example that prints the time according to the LeapC library.

It does not require a tracking camera or the Ultraleap Tracking service to be running.

This can be used to check if the python module has built successfully.
"""
import leap


def main():
    # Print the current time according to LeapC
    now = leap.get_now()
    print(now)


if __name__ == "__main__":
    main()
