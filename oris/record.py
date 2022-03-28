from band_detection import BandDetectionResult

import numpy as np
import datetime
import os
import pickle

RECORD_SAVE_PATH = './scan_record/'

class DetectionRecord:
    def __init__(self, image: np.ndarray, detection_result: BandDetectionResult,
                       time: datetime.datetime = None):
        """
        Initializes the DetectionRecord object.
        Args:
            image: The original image used for inference, to generate detection_result.
            detection_result: The BandDetectionResult object asscioated with image.
            time: The time at which the result is generated.
        """
        self.image = image
        self.detection_result = detection_result

        self.time = time
        if time is None:
            self.time = datetime.datetime.now()

    def save(self, filename: str = None):
        """
        Saves the pickle representation of this DetectionRecord object to a file.
        Args:
            filename: The filename of the save file to create.
        """
        os.makedirs(RECORD_SAVE_PATH, exist_ok=True)
        if filename is None:
            filename = '{}.pickle'.format(self.time.strftime('%Y-%m-%d_%H-%M-%S'))

        filepath = os.path.join(RECORD_SAVE_PATH, filename)
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

def read_from_file(filename: str) -> DetectionRecord:
    """
    Reads the DetectionRecord object from a save file.
    Returns:
        The read DetectionRecord object.
    """
    filepath = os.path.join(RECORD_SAVE_PATH, filename)
    with open(filepath, 'rb') as f:
        return pickle.load(f)
