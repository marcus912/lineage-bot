import os
import sys
import cv2 as cv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from src.core.detection.yolo_v2 import YoloDetection
from src.core.vision_v2 import Vision
from src.core.window_capture import WindowCapture
import pyautogui


def main():
    os.chdir(project_root)

    DEBUG = False

    # initialize the WindowCapture class
    wincap = WindowCapture()
    # load the detector
    detector = YoloDetection('models/yolo/la3-v3.pt', conf=0.75)
    # load an empty Vision class
    vision = Vision()

    wincap.start()

    while True:
        # if we don't have a screenshot yet, don't run the code below this point yet
        if wincap.screenshot is None:
            continue

        # give detector the current screenshot to search for objects in
        results = detector.predict(wincap.screenshot)
        coordinates = detector.plot_result(results[0])
        if len(coordinates) > 0:
            x, y, x2, y2, name, conf = coordinates[0]
            print(x, y, x2, y2, name, conf)
            pyautogui.moveTo(int(x + (x2-x)/2) + wincap.offset_x, y + (y2-y)/2 + wincap.offset_y, duration=0.05)
            pyautogui.mouseDown()
            pyautogui.sleep(3)
            pyautogui.mouseUp()

        if DEBUG:
            # draw the detection results onto the original image
            annotated_frame = vision.draw_rectangles(wincap.screenshot, coordinates)
            cv.imshow('Matches', annotated_frame)

        # press 'q' with the output window focused to exit.
        # waits 1 ms every loop to process key presses
        key = cv.waitKey(1)
        if key == ord('q'):
            wincap.stop()
            detector.stop()
            cv.destroyAllWindows()
            break

    print('Done.')


if __name__ == '__main__':
    main()
