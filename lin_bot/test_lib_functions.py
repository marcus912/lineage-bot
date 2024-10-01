from time import sleep
import cv2 as cv
import pyautogui
from windowcapture import WindowCapture
from detection import Detection
from vision import Vision

wincap = WindowCapture()
# detector = Detection(['cascade/cascade.xml'])
vision = Vision()

wincap.start()
# detector.start()

# wincap.offset_x, wincap.offset_y, wincap.w, wincap.h
while True:
    print('Move to my position {}, {}'.format(wincap.w/2, wincap.h/2))
    pyautogui.moveTo(x=wincap.w/2, y=wincap.h/2, duration=2)
    pyautogui.click(button='left')
    sleep(5)
