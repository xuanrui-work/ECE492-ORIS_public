# Copyright 2021 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utility functions to display the pose detection results."""

from typing import List

import cv2
import numpy as np
from object_detector import Detection

_MARGIN = 10  				# pixels
_ROW_SIZE = 10  			# pixels
_FONT_SIZE = 1
_FONT_THICKNESS = 1
_TEXT_COLOR = (255, 0, 0)	# red

def visualize(image: np.ndarray, detections: List[Detection]) -> np.ndarray:
	"""Draws bounding boxes on the input image and return it.
	Args:
		image: The input RGB image.
		detections: The list of all "Detection" entities to be visualize.

	Returns:
		Image with bounding boxes.
	"""
	for detection in detections:
		# Draw bounding_box
		start_point = detection.bounding_box.left, detection.bounding_box.top
		end_point = detection.bounding_box.right, detection.bounding_box.bottom
		cv2.rectangle(image, start_point, end_point, _TEXT_COLOR, 3)

		# Draw label and score
		category = detection.categories[0]
		class_name = category.label
		probability = round(category.score, 2)
		result_text = class_name + ' (' + str(probability) + ')'
		text_location = (_MARGIN + detection.bounding_box.left, _MARGIN + _ROW_SIZE + detection.bounding_box.top)
		cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN, _FONT_SIZE, _TEXT_COLOR, _FONT_THICKNESS)
	return image

import time
class FPSCounter:
	def __init__(self):
		self.t_start = time.time()
		self.t_stop = 0
		self.t_delta = 0

		self.count = 0
		self.UPDATE_INTERVAL = 10

		self.fps = 0

	def update(self):
		self.count += 1
		if self.count < self.UPDATE_INTERVAL:
			return
		self.t_stop = time.time()
		self.t_delta = self.t_stop - self.t_start

		self.fps = self.count / self.t_delta if self.t_delta else 0
		self.count = 0
		self.t_start = time.time()
	
	def draw_on_img(self, image: np.ndarray):
		text_location = (_MARGIN, _MARGIN + _ROW_SIZE*2)
		cv2.putText(image, f'FPS: {self.fps:.2f}', text_location, cv2.FONT_HERSHEY_PLAIN, _FONT_SIZE*2, _TEXT_COLOR, _FONT_THICKNESS)
