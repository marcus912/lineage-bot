import cv2 as cv
from threading import Thread, Lock


class Detection:

    # threading properties
    stopped = True
    lock = None
    rectangles = []
    # properties
    cascade = None
    cascades = []
    screenshot = None

    def __init__(self, model_file_paths):
        # create a thread lock object
        self.lock = Lock()
        # load the trained model
        # for model_file_path in model_file_paths:
        #     self.cascades.append(cv.CascadeClassifier(model_file_path))
        self.cascade = cv.CascadeClassifier(model_file_paths[0])

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
                # rectangles = []
                # for cascade in self.cascades:
                #     rectangles = cascade.detectMultiScale(self.screenshot)
                rectangles = self.cascade.detectMultiScale(self.screenshot)
                # You can adjust groupThreshold and eps based on your specific needs.
                # Increasing groupThreshold may merge more rectangles, while decreasing eps will make the grouping stricter.
                # rectangles, weights = cv2.groupRectangles(rectangles.tolist(), groupThreshold=1, eps=0.2)

                # if len(rectangles) > 0:
                #     print('Found {} targets'.format(len(rectangles)))

                # lock the thread while updating the results
                self.lock.acquire()
                self.rectangles = rectangles
                self.lock.release()
