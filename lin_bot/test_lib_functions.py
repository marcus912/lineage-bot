import cv2 as cv
from windowcapture import WindowCapture
from detection import Detection
from vision import Vision

wincap = WindowCapture()
detector = Detection(['cascade/cascade.xml'])
vision = Vision()

wincap.start()
detector.start()