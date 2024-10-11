from pathlib import Path
from detection_yolo import YoloDetection

wincap = WindowCapture()
detector = YoloDetection('stairs/best.pt')
vision = Vision()

wincap.start()
detector.start()

for result in results:
    boxes = result.boxes  # Boxes object for bounding box outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Probs object for classification outputs
    obb = result.obb  # Oriented boxes object for OBB outputs
    result.show()  # display to screen

