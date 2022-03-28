from typing import List, Tuple

import cv2
import numpy as np

CATEGORY_2_COLOR_DICT = {               # color format is in RGB
    'black_band':   (  0,   0,   0),
    'brown_band':   (102,  51,   0),
    'red_band':     (255,   0,   0),
    'orange_band':  (255, 128,   0),
    'yellow_band':  (255, 255,   0),
    'green_band':   (  0, 255,   0),
    'blue_band':    (  0,   0, 255),
    'violet_band':  (255,   0, 127),
    'grey_band':    (128, 128, 128),
    'white_band':   (255, 255, 255),
    'gold_band':    (255, 255, 153),
    'silver_band':  (224, 224, 224),
}

class Rectangle:
    def __init__(self, left: int, top: int, right: int, bottom: int,
                       color: Tuple[int] = (255, 0, 0), line_thickness: int = 1
        ):
        """
        Initializes the Rectangle object.
        Args:
            left, top, right, bottom: Coordinates of the rectangle.
            color: Color of the rectangle in BGR format.
            line_thickness: Thickness of the line of the rectangle.
        """
        self.left   = left
        self.top    = top
        self.right  = right
        self.bottom = bottom

        self.color  = color
        self.line_thickness = line_thickness

    def get_center_pt(self) -> List[int]:
        """
        Gets the center point of the rectangle.
        Returns:
            The center point in format [x, y].
        """
        x_center = self.left + (self.right - self.left) / 2
        y_center = self.top + (self.bottom - self.top) / 2
        return [round(x_center), round(y_center)]
    
    def draw_on_img(self, image: np.ndarray):
        """
        Draws the rectangle on an image.
        Args:
            image: Target image to draw on.
        """
        pt1 = (self.left, self.top)
        pt2 = (self.right, self.bottom)
        cv2.rectangle(image, pt1, pt2, self.color, self.line_thickness)

class DetectedObject:
    _BOUNDING_BOX_THICKNESS = 1

    _TEXT_MARGIN            = 10
    _TEXT_ROW_SIZE          = 10
    _TEXT_FONT_SIZE         = 1
    _TEXT_FONT_THICKNESS    = 1

    def __init__(self, id: int, label: str, score: float, bounding_box: Rectangle):
        """
        Initializes the DetectedObject object.
        Args:
            id: ID of detected object.
            label: Label of detected object.
            score: Score of detected object.
            bounding_box: Rectangle bounding box of detected object.
        """
        self.id = id
        self.label = label
        self.score = score
        self.bounding_box = bounding_box

    def get_center_pt(self) -> List[int]:
        """
        Gets the center point of the detected object.
        Returns:
            The center point in format [x, y].
        """
        return self.bounding_box.get_center_pt()
    
    def draw_bounding_box(self, image: np.ndarray):
        """
        Draws the bounding box of this object on an image.
        Args:
            image: Target image to draw on.
        """
        self.bounding_box.draw_on_img(image)
    
    def draw_statistics(self, image: np.ndarray):
        """
        Draws the detection statistics on an image.
        Args:
            image: Target image to draw on.
        """
        text = f'{self.label[0:2]}: {self.score:.2f}'
        text_org = (
            self._TEXT_MARGIN + self.bounding_box.left,
            self._TEXT_MARGIN + self._TEXT_ROW_SIZE + self.bounding_box.top
        )
        cv2.putText(
            image, text, text_org, cv2.FONT_HERSHEY_PLAIN,
            self._TEXT_FONT_SIZE,
            self.bounding_box.color,
            self._TEXT_FONT_THICKNESS
        )

class DetectedBand(DetectedObject):
    def __init__(self, id: int, label: str, score: float, bounding_box: List[int]):
        """
        Initializes the DetectedBand object.
        Args:
            id: ID of detected band.
            label: Label of detected band.
            score: Score of detected band.
            bounding_box: Coordinate of bounding box of detected band in [x1, y1, x2, y2].
        """
        super().__init__(id, label, score, Rectangle(
            bounding_box[0], bounding_box[1],
            bounding_box[2], bounding_box[3],
            CATEGORY_2_COLOR_DICT[label]
        ))
