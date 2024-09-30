import cv2 as cv
import os
from time import time
from windowcapture import WindowCapture

if not os.path.exists('screenshot/positive'):
    os.makedirs('screenshot/positive')
if not os.path.exists('screenshot/negative'):
    os.makedirs('screenshot/negative')

wincap = WindowCapture()
while(True):
    loop_time = time()
    screenshot = wincap.get_screenshot()
    cv.imshow('screen', screenshot)

    key = cv.waitKey(1)
    if key == ord('q'):
        cv.destroyAllWindows()
        print('End the task')
        break
    elif key == ord('f'):
        cv.imwrite('screenshot/positive/{}.png'.format(loop_time), screenshot)
        print('screenshot/positive image {}'.format(loop_time))
    elif key == ord('d'):
        cv.imwrite('screenshot/negative/{}.png'.format(loop_time), screenshot)
        print('screenshot/negative image {}'.format(loop_time))
print('Done.')
