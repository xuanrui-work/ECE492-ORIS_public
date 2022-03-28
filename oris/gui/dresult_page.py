from band_detection import BandDetectionResult
from resistor import Resistor, ResistorError
from record import DetectionRecord

from . import font

import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

class DResultPage(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: tk.Frame):
        """
        Initializes the DResultPage object, which is a tkinter frame for providing the detection result UI.
        """
        super().__init__(parent)
        self.parent = parent; self.controller = controller

        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=0, column=0, rowspan=1, sticky='nsew')
        self.canvas.image_container = None

        self.label = tk.Label(
            self, font=font.NORMAL_LABEL_FONT,
            anchor='nw',
            justify='left'
        )
        self.label.grid(row=1, column=0, rowspan=1, sticky='nsew')

        self.cont_button = tk.Button(
            self, font=font.NORMAL_BUTTON_FONT,
            text='Continue',
            command=self.controller.raise_main_page
        )
        self.cont_button.grid(row=1, column=1, sticky='nsew')

        self.contsave_button = tk.Button(
            self, font=font.NORMAL_BUTTON_FONT,
            text='Save & Continue',
            command=self.contsave_button_callback
        )
        self.contsave_button.grid(row=0, column=1, sticky='nsew')

        self.rowconfigure([0, 1], weight=1)
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=1)

        # member variables of this frame
        self.detection_image: np.ndarray           = None
        self.detection_result: BandDetectionResult = None

    def contsave_button_callback(self):
        detection_record = DetectionRecord(self.detection_image, self.detection_result)
        detection_record.save()
        self.controller.raise_main_page()

    def set_label_to_result(self, detection_result: BandDetectionResult):
        """
        Sets the label in this frame to format and display the corresponding detection result.
        Args:
            detection_result: The detection result to display.
        """
        labels = ', '.join([x.label[:-5] for x in detection_result.detected_bands])
        labels = f'[{labels}]'

        try:
            resistor    = Resistor(detection_result)
            resistence  = resistor.get_resistance()
            tolerance   = resistor.get_tolerance()
        except ResistorError as error:
            self.label.config(text=f'{str(error)}\nDetected bands: {labels}')
            self.contsave_button.config(state='disabled')
            return

        label_text = f'Detected Bands: {labels}\n' \
                     f'Resistence:     {resistence:,} Ohms\n' \
                     f'Tolerance:      {tolerance} %\n'
        self.label.config(text=label_text)
        self.contsave_button.config(state='normal')

    def set_canvas_to_image(self, image: np.ndarray):
        """
        Sets the canvas in this frame to format and display the corresponding image.
        Args:
            image: The image to display in the canvas.
        """
        pil_image = Image.fromarray(image, mode='RGB')
        image_tk = ImageTk.PhotoImage(pil_image)
        self.canvas.image_tk = image_tk

        if self.canvas.image_container is None:
            self.canvas.image_container = self.canvas.create_image(0, 0, anchor='nw', image=image_tk)
        else:
            self.canvas.itemconfig(self.canvas.image_container, image=image_tk)

    def set_result(self, image: np.ndarray, detection_result: BandDetectionResult):
        """
        Sets the result of this frame and update the UI on this frame to reflect the result.
        Args:
            image: The original image used for detection.
            detection_result: The detection result output from the inference.
        """
        self.detection_image  = image.copy()
        self.detection_result = detection_result

        self.detection_result.draw_on_img(image)
        self.set_canvas_to_image(image)
        self.set_label_to_result(self.detection_result)
