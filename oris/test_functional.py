from typing import Tuple

from object_detector import ObjectDetector, ObjectDetectorOptions
from band_detection import BandDetectionResult
from detected_object import DetectedBand

from camera_stream import CameraStreamThread
import utils

import tkinter as tk
import numpy as np
import cv2
from PIL import Image, ImageTk

TFLITE_MODEL_PATH = '../tflite_models/resistor_band_300x300_ssd_mobilenet_v2_320x320_coco17_tpu-8_aug1.tflite'

CAMERA_USE_VIDEO_PORT = True
CAMERA_ROTATION = 90

options = ObjectDetectorOptions(num_threads=4, score_threshold=0.4, max_results=5, enable_edgetpu=False)
detector = ObjectDetector(model_path=TFLITE_MODEL_PATH, options=options)

class SimpleORIS:
    def __init__(self, resolution: Tuple[int], fps: int):
        self.resolution = resolution
        self.fps = fps
        
        self.camera_thread = CameraStreamThread(self.resolution, self.fps)
        self.process_loop_delay = int(1000 / self.fps)
        
        self.inference_area = [375, 175, 300, 300]       # x, y, w, h of inference box
        self.run_inference  = True

        self.init_ui()
        self.fps_counter = utils.FPSCounter()
    
    def init_ui(self):
        self.root = tk.Tk()

        self.root.title('simple_oris')
        self.root.geometry(f'{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}')

        self.label = tk.Label(self.root, width=int(self.resolution[0] * 5/6), height=self.resolution[1])
        self.label.pack(side='left')

        self.close_button = tk.Button(self.root, text='Exit', command=self.close)
        self.close_button.pack(expand=True, fill='both', side='right')

        self.toggle_button = tk.Button(self.root, text='Toggle\nInference', bg='green', command=self.toggle_inference)
        self.toggle_button.pack(expand=True, fill='both', side='right')

    def start(self):
        self.camera_thread.start()
        self.label.after(0, self.process_image)
        self.root.mainloop()

    def close(self):
        self.camera_thread.signal_stop()
        self.camera_thread.join()
        self.root.destroy()

    def make_inference(self, image):
        detections = detector.detect(image)

        detected_bands = []
        for detection in detections:
            category = detection.categories[0]
            bounding_box = [
                detection.bounding_box.left, detection.bounding_box.top,
                detection.bounding_box.right, detection.bounding_box.bottom
            ]
            detected_bands.append(DetectedBand(category.index, category.label, category.score, bounding_box))

        result = BandDetectionResult(detected_bands)
        for band in result.detected_bands:
            band.draw_bounding_box(image)
            band.draw_statistics(image)
    
    def draw_inference_box(self, sub_image):
        white_rect = np.ones(sub_image.shape, dtype=np.uint8) * 255
        sub_image = cv2.addWeighted(sub_image, 0.5, white_rect, 0.5, 1.0)
        return sub_image

    def process_image(self):
        image = self.camera_thread.get_frame()
        if self.run_inference:
            x, y, w, h = self.inference_area
            self.make_inference(image[y:y+h, x:x+w])
            image[y:y+h, x:x+w] = self.draw_inference_box(image[y:y+h, x:x+w])
        
        self.fps_counter.update()
        self.fps_counter.draw_on_img(image)

        pil_image = Image.fromarray(image, mode='RGB')
        image_tk  = ImageTk.PhotoImage(pil_image)

        self.label.image_tk = image_tk
        self.label.configure(image=image_tk)

        self.label.update_idletasks()
        self.label.after(self.process_loop_delay, self.process_image)

    def toggle_inference(self):
        self.run_inference = not self.run_inference
        if self.run_inference:
            self.toggle_button.configure(bg='green')
        else:
            self.toggle_button.configure(bg='red')

if __name__ == '__main__':
    simple_oris = SimpleORIS((1280, 720), 30)
    simple_oris.start()
