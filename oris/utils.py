import cv2
import numpy as np
import time

class FPSCounter:
    _UPDATE_INTERVAL = 10

    _MARGIN         = 10            # pixels
    _ROW_SIZE       = 20            # pixels
    _FONT_SIZE      = 2
    _FONT_THICKNESS = 2
    _TEXT_COLOR     = (255, 0, 0)   # red

    def __init__(self):
        """
        Initializes the FPSCounter object.
        """
        self.count = 0
        self.fps = 0

        self.t_start = time.time()
        self.t_stop = 0
        self.t_delta = 0

    def update(self):
        """
        Updates the FPS counter and calculates the FPS from it.
        """
        self.count += 1
        if self.count < self._UPDATE_INTERVAL:
            return
        self.t_stop = time.time()
        self.t_delta = self.t_stop - self.t_start

        self.fps = self.count / self.t_delta if self.t_delta else 0
        self.count = 0
        self.t_start = time.time()

    def draw_on_img(self, image: np.ndarray):
        """
        Draws the FPS value onto an image.
        Args:
            image: Target image to draw on.
        """
        text_location = (self._MARGIN, self._MARGIN + self._ROW_SIZE)
        cv2.putText(
            image, f'FPS: {self.fps:.2f}', text_location,
            cv2.FONT_HERSHEY_PLAIN,
            self._FONT_SIZE,
            self._TEXT_COLOR,
            self._FONT_THICKNESS,
        )

    def update_and_draw(self, image: np.ndarray):
        """
        Updates the FPS counter, calculates the FPS from it,
        and draws the FPS value onto an image.
        Args:
            image: Target image to draw on.
        """
        self.update()
        self.draw_on_img(image)
