import cv2 as cv
from testimagedetection import ImageDetection
from vision import Vision
from pathlib import Path

detector = ImageDetection(['cascade/cascade.xml'])
vision = Vision()
pathlist = Path('positive').glob('*.png')

for path in pathlist:
    image_path = str(path)
    print(image_path)
    image = cv.imread(image_path, cv.IMREAD_UNCHANGED)
    detector.detect(image)

    detection_image = vision.draw_rectangles(image, detector.rectangles)
    # display the images
    cv.imshow('Matches', detection_image)
    key = cv.waitKey()
    if key == ord('n'):
        continue
    elif key == ord('q'):
        cv.destroyAllWindows()
        break
