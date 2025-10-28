from threading import Thread, Lock

from ultralytics import YOLO


class YoloDetection:
    # threading properties
    stopped = True
    lock = None
    rectangles = []
    screenshot = None
    model = None

    def __init__(self, model_path, interval=0, conf=0.6):
        self.lock = Lock()
        self.model = YOLO(model_path)
        self.model.fuse()
        self.interval = interval
        self.conf = conf

    def predict(self, frame):
        return self.model.predict(frame, verbose=True, conf=self.conf)

    def plot_bboxes(self, results):
        rectangles = []
        for result in results:
            boxes = result.boxes.cpu().numpy()
            xyxys = boxes.xyxy
            for i in range(len(xyxys)):
                xyxy = xyxys[i]
                x = int(xyxy[0])
                y = int(xyxy[1])
                w = int(xyxy[2]) - int(xyxy[0])
                h = int(xyxy[3]) - int(xyxy[1])
                rectangles.append([x, y, w, h, result.names[int(boxes.cls[i])]])
        return rectangles

    def plot_result(self, result):
        boxes = result.boxes.cpu().numpy()
        xyxys = boxes.xyxy
        targets = []
        for i in range(len(xyxys)):
            xyxy = xyxys[i]
            x = int(xyxy[0])
            y = int(xyxy[1])
            x2 = int(xyxy[2])
            y2 = int(xyxy[3])
            targets.append([x, y, x2, y2, result.names[int(boxes.cls[i])], boxes.conf[i]])
        return targets

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
                results = self.predict(self.screenshot)
                rectangles = self.plot_bboxes(results)
                # lock the thread while updating the results
                self.lock.acquire()
                self.rectangles = rectangles
                self.lock.release()
