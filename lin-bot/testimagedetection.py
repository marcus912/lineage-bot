import cv2 as cv


class ImageDetection:
    rectangles = []
    # properties
    cascade = None

    def __init__(self, model_file_paths):
        self.cascade = cv.CascadeClassifier(model_file_paths[0])


    def detect(self, image):
        self.rectangles = self.cascade.detectMultiScale(image)
