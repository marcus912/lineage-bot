import os

import cv2 as cv

from detection_yolo_v2 import YoloDetection
from vision_v2 import Vision
from windowcapture import WindowCapture
import pyautogui

os.chdir(os.path.dirname(os.path.abspath(__file__)))


DEBUG = False

# initialize the WindowCapture class
wincap = WindowCapture()
# load the detector
detector = YoloDetection('model/yolo/la3-v3.pt', conf=0.75)
# load an empty Vision class
vision = Vision()

wincap.start()
# detector.start()


while True:
    # if we don't have a screenshot yet, don't run the code below this point yet
    if wincap.screenshot is None:
        continue

    # give detector the current screenshot to search for objects in
    # detector.update(wincap.screenshot)
    results = detector.predict(wincap.screenshot)
    # annotated_frame = results[0].plot()
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
        # detection_image = vision.draw_rectangles(wincap.screenshot, detector.rectangles)
        # display the images
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
