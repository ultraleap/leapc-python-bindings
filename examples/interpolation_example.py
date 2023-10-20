"""Uses interpolation in Leap API to determine the location of hands based on 
previous data. We use the LatestEventListener to wait until we have tracking 
events. We delay by 0.02 seconds each frame to simulate some delay, we get a 
frame size of the frame closest to the time we want to interpolate from and 
then interpolate on that frame"""
import leap
import time
from timeit import default_timer as timer
from typing import Callable
from leap.events import TrackingEvent
from leap.event_listener import LatestEventListener
from leap.datatypes import FrameData


def wait_until(condition: Callable[[], bool], timeout: float = 5, poll_delay: float = 0.01):
    start_time = timer()
    while timer() - start_time < timeout:
        if condition():
            return True
        time.sleep(poll_delay)
    if not condition():
        return False


def main():
    tracking_listening = LatestEventListener(leap.EventType.Tracking)

    connection = leap.Connection()
    connection.add_listener(tracking_listening)

    with connection.open() as open_connection:
        wait_until(lambda: tracking_listening.event is not None)
        # ctr-c to exit
        while True:
            event = tracking_listening.event
            if event is None:
                continue
            event_timestamp = event.timestamp

            target_frame_size = leap.ffi.new("uint64_t*")
            frame_time = leap.ffi.new("int64_t*")
            frame_time[0] = event_timestamp

            # simulate 20 ms delay
            time.sleep(0.02)

            try:
                # we need to query the storage required for our interpolation
                # request, the size will depend on the number visible hands in
                # this frame
                leap.get_frame_size(open_connection, frame_time, target_frame_size)
            except Exception as e:
                print("get_frame_size() failed with: ", e)
                continue

            frame_data = FrameData(target_frame_size[0])
            try:
                # actually interpolate and get frame data from the Leap API
                # this is the time of the frame plus the 20ms artificial
                # delay and an estimated 10ms processing time which should
                # get close to real time hand tracking with interpolation
                leap.interpolate_frame(
                    open_connection,
                    event_timestamp + 30000,
                    frame_data.frame_ptr(),
                    target_frame_size[0],
                )
            except Exception as e:
                print("interpolate_frame() failed with: ", e)
                continue

            event = TrackingEvent(frame_data)
            print(
                "Frame ",
                event.tracking_frame_id,
                " with ",
                len(event.hands),
                "hands with a delay of ",
                leap.get_now() - event.timestamp,
            )
            for hand in event.hands:
                hand_type = "left" if str(hand.type) == "HandType.Left" else "right"
                print(
                    f"Hand id {hand.id} is a {hand_type} hand with position ({hand.palm.position.x}, {hand.palm.position.y}, {hand.palm.position.z})."
                )


if __name__ == "__main__":
    main()
