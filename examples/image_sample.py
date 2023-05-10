import leap
import time


class MyListener(leap.Listener):
    def on_connection_event(self, event):
        print("Connected")

    def on_device_event(self, event):
        print(f"Found device {str(event.device().serial())}")

    def on_tracking_event(self, event):
        print(f"Frame {str(event.tracking_frame_id)} with {str(len(event.hands))} hands.")
        for hand in event.hands:
            hand_type = "left" if str(hand.type) == "HandType.Left" else "right"
            print(f"Hand id {str(hand.id)} is a {hand_type} hand with position ({str(hand.palm.position.x)}, {str(hand.palm.position.y)}, {str(hand.palm.position.z)}).")


def main():
    my_listener = MyListener()

    connection = leap.Connection()
    connection.add_listener(my_listener)

    running = True

    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)
        while running:
            time.sleep(1)


if __name__ == "__main__":
    main()
