import cv2 as cv
from time import time
from windowcapture import WindowCapture

wincap = WindowCapture()
while(True):
    loop_time = time()
    screenshot = wincap.get_screenshot()
    cv.imshow('screen', screenshot)

    key = cv.waitKey(1)
    if key == ord('q'):
        cv.destroyAllWindows()
        break
    elif key == ord('f'):
        cv.imwrite('positive/{}.png'.format(loop_time), screenshot)
        print('write a positive image')
    elif key == ord('d'):
        cv.imwrite('negative/{}.png'.format(loop_time), screenshot)
        print('write a negative image')
print('Done.')
