import cv2 as cv
from windowcapture import WindowCapture
from detection import Detection
from vision import Vision

wincap = WindowCapture()
detector = Detection(['cascade/cascade.xml'])
vision = Vision()

wincap.start()
detector.start()

while(True):

    # if we don't have a screenshot yet, don't run the code below this point yet
    if wincap.screenshot is None:
        continue
    detector.update(wincap.screenshot)
    # draw the detection results onto the original image
    detection_image = vision.draw_rectangles(wincap.screenshot, detector.rectangles)
    # display the images
    cv.imshow('Matches', detection_image)
    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    key = cv.waitKey(1)
    if key == ord('q'):
        wincap.stop()
        detector.stop()
        cv.destroyAllWindows()
        break
