import configargparse
import cv2 as cv
import math
import threading

from pyparrot.Bebop import Bebop
from pyparrot.DroneVision import DroneVision
from gestures.gesture_controller import GestureController
from utils import CvFpsCalc
from gestures import *



def get_args():
    print('## Reading configuration ##')
    parser = configargparse.ArgParser(default_config_files=['config.txt'])

    parser.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')
    parser.add("--device", type=int)
    parser.add("--width", help='cap width', type=int)
    parser.add("--height", help='cap height', type=int)
    parser.add('--use_static_image_mode', action='store_true', help='True if running on photos')
    parser.add("--min_detection_confidence",
               help='min_detection_confidence',
               type=float)
    parser.add("--min_tracking_confidence",
               help='min_tracking_confidence',
               type=float)
    parser.add("--buffer_len",
               help='Length of gesture buffer',
               type=int)

    args = parser.parse_args()

    return args

def main():
    # init global vars
    global gesture_buffer
    global gesture_id

    # Argument parsing
    args = get_args()
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 640
    in_flight = False

    # Camera preparation
    bebop = Bebop(drone_type='Bebop2')
    success = bebop.connect(5)
    bebop.start_video_stream()

    # cap = tello.get_frame_read()
    cap = cv.VideoCapture(1)
    cap.set(3, FRAME_WIDTH)
    cap.set(4, FRAME_HEIGHT)
    cap.set(10, 150)

    # Init Tello Controllers
    gesture_controller = GestureController(bebop)
    gesture_detector = GestureRecognition(args.use_static_image_mode, args.min_detection_confidence,
                                          args.min_tracking_confidence)
    gesture_buffer = GestureBuffer(buffer_len=args.buffer_len)

    def tello_control(gesture_controller):
        global gesture_buffer

        gesture_controller.gesture_control(gesture_buffer)

    # FPS Measurement
    cv_fps_calc = CvFpsCalc(buffer_len=10)

    mode = 0
    number = -1

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
        threading.Thread(target=tello_control, args=(gesture_controller,)).start()

        debug_image = gesture_detector.draw_info(debug_image, fps, mode, number)
        cv.imshow('Tello Gesture Recognition', debug_image)

    bebop.smart_sleep(5)
    bebop.safe_land(10)
    bebop.disconnect()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()