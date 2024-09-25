import cv2 as cv
from time import time
from windowcapture import WindowCapture

wincap = WindowCapture()
loop_time = time()
while(True):
    screenshot = wincap.get_screenshot()
    cv.imshow('screen', screenshot)

    key = cv.waitKey(1)
    if key == ord('q'):
        cv.destroyAllWindows()
        break
    elif key == ord('f'):
        cv.imwrite('positive/{}.png'.format(loop_time), screenshot)
    elif key == ord('d'):
        cv.imwrite('negative/{}.png'.format(loop_time), screenshot)
