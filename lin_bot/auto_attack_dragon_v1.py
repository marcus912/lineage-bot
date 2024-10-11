import os

import cv2 as cv

from bot_dragon6 import Dragon6Bot, BotState
from detection import Detection
from lin_bot.detection_yolo import YoloDetection
from vision import Vision
from windowcapture import WindowCapture

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their
# own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))


DEBUG = True

# initialize the WindowCapture class
wincap = WindowCapture()
# load the detector
detector = Detection('model/cascade_dragon6/cascade.xml', 1.05, 6, (90, 110), (35, 35))
# load yolo model
stair_detector = YoloDetection('model/yolo/stairs.pt')
# load an empty Vision class
vision = Vision()
# initialize the bot
bot = Dragon6Bot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h))

wincap.start()
detector.start()
stair_detector.start()
bot.start()

while True:
    # if we don't have a screenshot yet, don't run the code below this point yet
    if wincap.screenshot is None:
        continue

    # give detector the current screenshot to search for objects in
    detector.update(wincap.screenshot)
    stair_detector.update(wincap.screenshot)
    # sleep(0.1)

    # update the bot with the data it needs right now
    if bot.state == BotState.INITIALIZING:
        # while bot is waiting to start, go ahead and start giving it some targets to work
        # on right away when it does start
        targets = vision.get_click_points(detector.rectangles)
        stair_targets = vision.get_click_points(stair_detector.rectangles)
        bot.update_targets(targets, stair_targets)
    elif bot.state == BotState.SEARCHING:
        # when searching for something to click on next, the bot needs to know what the click
        # points are for the current detection results. it also needs an updated screenshot
        # to verify the hover tooltip once it has moved the mouse to that position
        targets = vision.get_click_points(detector.rectangles)
        stair_targets = vision.get_click_points(stair_detector.rectangles)
        bot.update_targets(targets, stair_targets)
        bot.update_screenshot(wincap.screenshot)
    elif bot.state == BotState.MOVING:
        # when moving, we need fresh screenshots to determine when we've stopped moving
        bot.update_screenshot(wincap.screenshot)
    elif bot.state == BotState.MINING:
        # nothing is needed while we wait for the mining to finish
        pass

    if DEBUG:
        # draw the detection results onto the original image
        detection_image = vision.draw_rectangles(wincap.screenshot, detector.rectangles)
        detection_image = vision.draw_rectangles(detection_image, stair_detector.rectangles)
        # display the images
        cv.imshow('Matches', detection_image)

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    key = cv.waitKey(1)
    if key == ord('q'):
        wincap.stop()
        detector.stop()
        bot.stop()
        cv.destroyAllWindows()
        break
    elif key == ord('p'):
        bot.stop()
        print('bot is pausing')
        continue
    elif key == ord('c'):
        bot.start()

print('Done.')
