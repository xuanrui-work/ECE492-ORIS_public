from typing import Tuple

import picamera
import numpy as np
import threading

import logging
logger = logging.getLogger(__name__)

CAMERA_USE_VIDEO_PORT = True
CAMERA_ROTATION = 90

class CameraStreamThread(threading.Thread):
    def __init__(self, resolution: Tuple[int], fps: int):
        """
        Initializes the CameraStreamThread object.
        Args:
            resolution: The resolution for camera capturing given by a tuple of (width, height).
            fps: The frames per second for camera capturing.
        """
        super().__init__()
        self.resolution = resolution
        self.fps = fps

        self.e_stop    = threading.Event()
        self.e_suspend = threading.Event()
        self.e_resume  = threading.Event()

        self.camera = picamera.PiCamera()
        self.camera.resolution = self.resolution
        self.camera.framerate = self.fps
        self.camera.rotation = CAMERA_ROTATION

        self.buffer = np.empty((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        self.frame  = self.buffer.copy()
    
    def run(self):
        """
        Overrides the run() method in the threading.Thread superclass.
        Runs the mainloop of this object.
        """
        logger.info('CameraStreamThread started.')

        for frame in self.camera.capture_continuous(self.buffer, format='rgb', use_video_port=CAMERA_USE_VIDEO_PORT):
            if self.e_stop.is_set():
                break
            elif self.e_suspend.is_set():
                self.e_resume.wait()
            else:
                self.frame = self.buffer.copy()

        self.camera.close()
        logger.info('CameraStreamThread ended.')

    def signal_stop(self):
        """
        Sends stop signal to this thread to terminate it.
        """
        self.signal_resume()
        self.e_stop.set()
    def signal_suspend(self):
        """
        Sends suspend signal to this thread to suspend it.
        """
        self.e_suspend.set()
        self.e_resume.clear()
    def signal_resume(self):
        """
        Sends resume signal to this thread to resume it.
        """
        self.e_suspend.clear()
        self.e_resume.set()

    def get_frame(self) -> np.ndarray:
        """
        Gets the most recently captured frame from the camera.
        Returns:
            The most recently captured frame.
        """
        return self.frame
