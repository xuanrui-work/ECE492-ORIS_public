from camera_stream import CameraStreamThread
from band_detection import BandDetectionResult, BandDetectionProcess
from utils import FPSCounter
from . import font

import multiprocessing

import tkinter as tk
import numpy as np
import cv2
from PIL import Image, ImageTk

class MainPage(tk.Frame):
    _CAMERA_RESOLUTION    = (1280, 720)
    _CAMERA_FPS           = 30
    _INFERENCE_AREA       = [375, 175, 300, 300]    # the rectangle with [x, y, w, h] on the image to run the inference on
    _INFERENCE_AREA_FM    = [200, 100]              # the focusmode inference area in the format [w, h]
    _STABILIZATION_CYCLES = 3                       # the number of inference cycles the detection result has to stabilize to be taken as the final result

    def __init__(self, parent: tk.Frame, controller: tk.Frame):
        """
        Initializes the MainPage object, which is a tkinter frame for providing the main UI.
        """
        super().__init__(parent)
        self.parent = parent; self.controller = controller

        self.canvas = tk.Canvas(self)
        self.canvas.bind('<Button-1>', self.canvas_onclick_callback)

        self.canvas.grid(row=0, column=0, rowspan=2, sticky='nsew')
        self.canvas_image_container = None

        self.exit_button = tk.Button(
            self, font=font.NORMAL_BUTTON_FONT,
            text='Exit',
            command=self.controller.close
        )
        self.exit_button.grid(row=1, column=1, sticky='nsew')

        self.config_button = tk.Button(
            self, font=font.NORMAL_BUTTON_FONT,
            text='Configurations',
            command=self.controller.raise_config_page
        )
        self.config_button.grid(row=0, column=1, sticky='nsew')

        self.rowconfigure([0, 1], weight=1)
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=1)

        # member variables of this frame 
        self.camera_thread = CameraStreamThread(self._CAMERA_RESOLUTION, self._CAMERA_FPS)
        self.process_loop_delay = int(1000 / self._CAMERA_FPS)

        self.p_conn, self.c_conn = multiprocessing.Pipe(duplex=True)
        self.inference_proc = BandDetectionProcess(self.c_conn)

        self.last_detection_image: np.ndarray = None
        self.last_detection_result: BandDetectionResult = None

        self.last_stable_detection: BandDetectionResult = None
        self.stable_count = 0

        self.e_suspend_processing = True
        self.e_focusmode = False
        self.fps_counter = FPSCounter()

    def canvas_onclick_callback(self, event):
        self.e_focusmode = not self.e_focusmode

    def update_canvas_to_image(self, image: np.ndarray):
        """
        Updates the canvas in this frame to format and display the corresponding image.
        Args:
            image: The image to display in the canvas.
        """
        pil_image = Image.fromarray(image, mode='RGB')
        image_tk = ImageTk.PhotoImage(pil_image)
        self.canvas.image_tk = image_tk

        if self.canvas_image_container is None:
            self.canvas_image_container = self.canvas.create_image(0, 0, anchor='nw', image=image_tk)
        else:
            self.canvas.itemconfig(self.canvas_image_container, image=image_tk)

    def draw_inference_box(self, image, x, y, w, h):
        """
        Draws a half-transparent inference box (rectangle) onto the image.
        Args:
            image: Target image to draw on.
            x, y, w, h: The left-top coordinate and dimension of the box.
        """
        white_rect = np.ones((h, w, 3), dtype=np.uint8) * 255
        image[y:y+h, x:x+w] = cv2.addWeighted(image[y:y+h, x:x+w], 0.5, white_rect, 0.5, 1.0)

    def process_result(self):
        """
        Processes last detection result obtained from the last detection image and invokes the result
        page to show the detection result if applicable.
        """
        if self.last_detection_result is None:
            return
        if not self.last_detection_result.is_valid():
            return

        if (self.last_stable_detection is not None) and (self.last_stable_detection.is_identical(self.last_detection_result)):
            self.stable_count += 1
        else:
            self.last_stable_detection = self.last_detection_result
            #self.stable_count = 0
            return

        if self.stable_count > self._STABILIZATION_CYCLES:
            self.stable_count = 0
            self.controller.dresult_page.set_result(self.last_detection_image, self.last_detection_result)
            self.controller.raise_dresult_page()

    def process_image(self):
        """
        Captures the image from the camera thread, sends it to the detection process if applicable,
        and updates the UI to show the last detection result.
        """
        image = self.camera_thread.get_frame()

        x, y, w, h = self._INFERENCE_AREA
        sub_image = image[y:y+h, x:x+w]

        if self.p_conn.poll():
            self.last_detection_result = self.p_conn.recv()
            self.process_result()

        if self.inference_proc.is_recv_ready():
            self.p_conn.send(sub_image)
            self.last_detection_image = sub_image.copy()

        self.draw_inference_box(image, x, y, w, h)

        if self.last_detection_result is not None:
            self.last_detection_result.draw_on_img(sub_image)

        self.fps_counter.update_and_draw(image)
        self.update_canvas_to_image(image)

    def process_image_focusmode(self):
        """
        The focusmode version of process_image(). This function uses a smaller inference area centered within
        the original inference area for detection.
        """
        image = self.camera_thread.get_frame()

        x, y, w, h = self._INFERENCE_AREA
        sub_image = image[y:y+h, x:x+w]

        w_fm, h_fm = self._INFERENCE_AREA_FM
        x_fm = padding_x = round((w - w_fm) / 2)
        y_fm = padding_y = round((h - h_fm) / 2)

        fm_image = cv2.copyMakeBorder(
            sub_image[y_fm:y_fm+h_fm, x_fm:x_fm+w_fm],
            padding_y, padding_y,
            padding_x, padding_x,
            cv2.BORDER_CONSTANT, value=(128, 128, 128)
        )

        if self.p_conn.poll():
            self.last_detection_result = self.p_conn.recv()
            self.process_result()

        if self.inference_proc.is_recv_ready():
            self.p_conn.send(fm_image)
            self.last_detection_image = sub_image.copy()

        self.draw_inference_box(image, x+x_fm, y+y_fm, w_fm, h_fm)

        if self.last_detection_result is not None:
            self.last_detection_result.draw_on_img(sub_image)

        self.fps_counter.update_and_draw(image)
        self.update_canvas_to_image(image)

    def process_loop(self):
        """
        The process loop for capturing and inferencing image, processing the detection result, and
        updating the UI.
        """
        if not self.e_suspend_processing:
            if self.e_focusmode:
                self.process_image_focusmode()
            else:
                self.process_image()
            self.after(self.process_loop_delay, self.process_loop)

    def tkraise(self):
        """
        Overrides the tkraise() method in the tk.Frame superclass.
        Raises this frame to the top.
        """
        if not self.camera_thread.is_alive():
            self.camera_thread.start()
        else:
            self.camera_thread.signal_resume()

        if not self.inference_proc.is_alive():
            self.inference_proc.start()
        else:
            while self.p_conn.poll():
                self.p_conn.recv()

        self.after(0, self.process_loop)
        self.e_suspend_processing = False
        super().tkraise()

    def suspend_processing(self):
        """
        Suspends the capture and inference of the image.
        """
        self.camera_thread.signal_suspend()
        self.e_suspend_processing = True

    def close(self):
        """
        Closes this MainPage object and releases all its resources.
        """
        if self.camera_thread.is_alive():
            self.camera_thread.signal_stop()
            self.camera_thread.join()

        if self.inference_proc.is_alive():
            self.inference_proc.signal_stop()
            self.inference_proc.join()
