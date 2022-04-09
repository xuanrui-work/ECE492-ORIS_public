from typing import List

import numpy as np

from object_detector import ObjectDetectorOptions, ObjectDetector
from detected_object import DetectedBand

import multiprocessing
import multiprocessing.connection

import ctypes
import statistics

import logging
logger = logging.getLogger(__name__)

TFLITE_MODEL_PATH = '../tflite_models/resistor_band_300x300_ssd_mobilenet_v2_320x320_coco17_tpu-8_aug3.tflite'

class BandDetectionResult:
    _STDEV_THRESHOLD_X = 15
    _STDEV_THRESHOLD_Y = 20

    def __init__(self, detected_bands: List[DetectedBand]):
        """
        Initializes the BandDetectionResult object.
        Args:
            detected_bands: List of DetectedBand objects containing detection result.
        """
        self.detected_bands = detected_bands
        self.sort_bands()

    def sort_bands(self, reverse=False):
        """
        Sorts the detected_bands list according to the bounding box center pt x-coordinate of each band.
        """
        self.detected_bands.sort(key=lambda x: x.bounding_box.get_center_pt()[0], reverse=reverse)

    def is_valid(self) -> bool:
        """
        Returns whether this BandDetectionResult object represents a valid resistor.
        """
        if len(self.detected_bands) < 4 or len(self.detected_bands) > 5:
            return False

        # check coordinate variations
        x_coord = [x.get_center_pt()[0] for x in self.detected_bands]
        y_coord = [x.get_center_pt()[1] for x in self.detected_bands]

        delta_x = []
        for i in range(len(self.detected_bands) - 1):
            delta_x.append(x_coord[i + 1] - x_coord[i])
        
        if statistics.stdev(delta_x) > self._STDEV_THRESHOLD_X:
            return False
        if statistics.stdev(y_coord) > self._STDEV_THRESHOLD_Y:
            return False
        return True
    
    def is_identical(self, other: 'BandDetectionResult') -> bool:
        """
        Returns whether this BandDetectionResult object represents the same resistor as other.
        """
        if not self.is_valid() or not other.is_valid():
            return False
        if len(self.detected_bands) != len(other.detected_bands):
            return False
        
        for i in range(len(self.detected_bands)):
            if self.detected_bands[i].label != other.detected_bands[i].label:
                return False
        return True
    
    def draw_on_img(self, image: np.ndarray):
        """
        Draws all detection results contained in this object on an image.
        Args:
            image: Target image to draw on.
        """
        for band in self.detected_bands:
            band.draw_bounding_box(image)
            band.draw_statistics(image)

class BandDetectionProcess(multiprocessing.Process):
    def __init__(self, conn: multiprocessing.connection.Connection):
        """
        Initializes the BandDetectionProcess object.
        Args:
            conn: The Connection object for receiving inputs and sending outputs.
        Notes:
            conn must be duplex. For conn, its input is the image to perform the detection upon,
            and its output is the BandDetectionResult object containing the detection results.
        """
        super().__init__()
        self.conn = conn
        self.e_stop = multiprocessing.Event()
        self.s_recv_ready = multiprocessing.Value(ctypes.c_bool, True, lock=False)

        self.options = ObjectDetectorOptions(num_threads=3, score_threshold=0.3, max_results=5, enable_edgetpu=False)
        self.detector = ObjectDetector(model_path=TFLITE_MODEL_PATH, options=self.options)
    
    def run(self):
        """
        Overrides the run() method in the multiprocessing.Process superclass.
        Runs the mainloop of this object.
        """
        logger.info('BandDetectionProcess started.')

        while not self.e_stop.is_set():
            if not self.conn.poll(1):
                continue
            self.s_recv_ready.value = False

            image = self.conn.recv()
            detections = self.detector.detect(image)

            detected_bands = []
            for detection in detections:
                category = detection.categories[0]
                bounding_box = [
                    detection.bounding_box.left, detection.bounding_box.top,
                    detection.bounding_box.right, detection.bounding_box.bottom
                ]
                detected_bands.append(DetectedBand(category.index, category.label, category.score, bounding_box))
            
            result = BandDetectionResult(detected_bands)
            self.conn.send(result)
            self.s_recv_ready.value = True

        logger.info('BandDetectionProcess ended.')

    def signal_stop(self):
        """
        Sends stop signal to this process to terminate it.
        """
        self.e_stop.set()
    def is_recv_ready(self) -> bool:
        """
        Returns whether this BandDetectionProcess is ready to process more data.
        Notes:
            Use this function to determine when to send an item onto conn.
        """
        return self.s_recv_ready.value
