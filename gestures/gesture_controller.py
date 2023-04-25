from pyparrot.Bebop import Bebop

class GestureController:
    def __init__(self, device: Bebop):
        self.bebop = device
        self._is_landing = False

    def gesture_control(self, gesture_buffer):
        gesture_id = gesture_buffer.get_gesture()
        # print("GESTURE", gesture_id)

        if not self._is_landing:
            if gesture_id == 0:  # Forward
                self.bebop.fly_direct(
                    roll=0,
                    pitch=50,
                    yaw=0,
                    vertical_movement=0,
                    duration=1
                )
                print('Move Forward')
            elif gesture_id == 1:  # STOP
                self.bebop.fly_direct(
                    roll=0,
                    pitch=0,
                    yaw=0,
                    vertical_movement=0,
                    duration=2
                )
                print('Stop')
            if gesture_id == 5:  # Back
                self.bebop.fly_direct(
                    roll=0,
                    pitch=-50,
                    yaw=0,
                    vertical_movement=0,
                    duration=0.5
                )
                print('Move Back')

            elif gesture_id == 2:  # UP
                self.bebop.fly_direct(
                    roll=0,
                    pitch=0,
                    yaw=0,
                    vertical_movement=50,
                    duration=1
                )
                print('Move UP')
            elif gesture_id == 4:  # DOWN
                self.bebop.fly_direct(
                    roll=0,
                    pitch=0,
                    yaw=0,
                    vertical_movement=-50,
                    duration=1
                )
                print('Move Down')

            elif gesture_id == 3:  # LAND
                self._is_landing = True
                self.bebop.safe_land(10)
                print('Land')

            elif gesture_id == 6: # LEFT
                self.bebop.fly_direct(
                    roll=50,
                    pitch=0,
                    yaw=0,
                    vertical_movement=0,
                    duration=1
                )
                print('Move Left')
            elif gesture_id == 7: # RIGHT
                self.bebop.fly_direct(
                    roll=-50,
                    pitch=0,
                    yaw=0,
                    vertical_movement=0,
                    duration=1
                )
                print('Move Right')

            elif gesture_id == -1:
                self.bebop.fly_direct(
                    roll=0,
                    pitch=0,
                    yaw=0,
                    vertical_movement=0,
                    duration=2
                )
                print('Do Nothing')