
import cv2 as cv
import math
import threading

from pyparrot.Bebop import Bebop
from pyparrot.DroneVision import DroneVision
from gestures.gesture_controller import GestureController
from utils import CvFpsCalc
from gestures import *
from voice import PorcupineThread

def main():
    # init global vars
    global gesture_buffer
    global gesture_id

    # Argument parsing
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 640
    in_flight = False

    # Starting voice control
    print('Starting Voice Control...')
    porcupine_thread = PorcupineThread(access_key='tHwfakI2LOhb/1l09yRCc22zakbkuNTZSb5RTmxsjC5NZdPk6jaWnQ==',
                                       device_index=-1,
                                       keyword_var=['./model/stop-device_en_mac_v2_2_0.ppn'])
    porcupine_thread.start()

    # Camera preparation
    print('Connecting...')
    bebop = Bebop()
    success = bebop.connect(10)
    print(success)
    bebop.start_video_stream()

    cap = cv.VideoCapture(0)
    cap.set(3, FRAME_WIDTH)
    cap.set(4, FRAME_HEIGHT)
    cap.set(10, 150)

    # Init Tello Controllers
    gesture_controller = GestureController(bebop)
    gesture_detector = GestureRecognition(False, 0.7, 0.5)
    gesture_buffer = GestureBuffer(buffer_len=5)

    def bebop_control(gesture_controller):
        global gesture_buffer

        gesture_controller.gesture_control(gesture_buffer)

    # FPS Measurement
    cv_fps_calc = CvFpsCalc(buffer_len=10)

    mode = 0
    number = -1
    
    print('Take Off')
    bebop.move_relative(0, 0, 10, math.radians(0))

    while cap.isOpened():
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 32: #Space
            if not in_flight:
                bebop.smart_sleep(5)
                bebop.safe_takeoff(10)
                in_flight = True
            elif in_flight:
                bebop.smart_sleep(5)
                bebop.safe_land(10)
                in_flight = False
        
        fps = cv_fps_calc.get()

        # Camera capture
        success, img = cap.read()
        debug_image, gesture_id = gesture_detector.recognize(img, number, mode)
        gesture_buffer.add_gesture(gesture_id)

        # Start control thread
        threading.Thread(target=bebop_control, args=(gesture_controller,)).start()

        debug_image = gesture_detector.draw_info(debug_image, fps, mode, number)
        cv.imshow('Gesture Recognition', debug_image)

    bebop.smart_sleep(5)
    bebop.safe_land(10)
    bebop.disconnect()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()