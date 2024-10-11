from threading import Thread, Lock

import cv2 as cv


class Detection:

    # threading properties
    stopped = True
    lock = None
    rectangles = []
    # properties
    cascade = None
    screenshot = None
    scale_factor = None
    min_neighbors = None
    max_size = None
    min_size = None

    def __init__(self, model_file_path, scale_factor, min_neighbors, max_size, min_size):
        # create a thread lock object
        self.lock = Lock()
        # load the trained model
        # for model_file_path in model_file_paths:
        #     self.cascades.append(cv.CascadeClassifier(model_file_path))
        self.cascade = cv.CascadeClassifier(model_file_path)
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.max_size = max_size
        self.min_size = min_size

    def update(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        # TODO: you can write your own time/iterations calculation to determine how fast this is
        while not self.stopped:
            if not self.screenshot is None:
                # do object detection

                rectangles = self.cascade.detectMultiScale(self.screenshot, scaleFactor=self.scale_factor, minNeighbors=self.min_neighbors,
                                                           minSize=self.min_size, maxSize=self.max_size)
                # You can adjust groupThreshold and eps based on your specific needs.
                # Increasing groupThreshold may merge more rectangles, while decreasing eps will make the grouping stricter.
                # rectangles, weights = cv2.groupRectangles(rectangles.tolist(), groupThreshold=1, eps=0.2)

                # if len(rectangles) > 0:
                #     print('Found {} targets'.format(len(rectangles)))

                # lock the thread while updating the results
                self.lock.acquire()
                self.rectangles = rectangles
                self.lock.release()
