import cv2 as cv
from pathlib import Path
from detection_yolo import YoloDetection
from vision import Vision

model_folder = 'la3'
pathlist = Path('{}/positive'.format(model_folder)).glob('*.png')
vision = Vision()
detector = YoloDetection('{}/la3-v3.pt'.format(model_folder))
#la3\positive\1728846473.2100644.png
for path in pathlist:
    image_path = str(path)
    print(image_path)
    image = cv.imread('image_path', cv.IMREAD_UNCHANGED)
    results = detection_image = detector.predict(image)
    rectangles = detector.plot_bboxes(results)
    print('rectangles size: ', len(rectangles))
    detection_image = vision.draw_rectangles(image, rectangles)
    # display the images
    cv.imshow('Matches', detection_image)
    key = cv.waitKey()
    if key == ord('n'):
        continue
    elif key == ord('q'):
        cv.destroyAllWindows()
        break
