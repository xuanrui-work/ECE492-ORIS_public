from typing import Tuple

import tkinter as tk
import picamera
import numpy as np

import cv2
from PIL import Image, ImageTk

import datetime
import os

CAMERA_USE_VIDEO_PORT = True
CAMERA_ROTATION = 90
IMAGE_SAVE_PATH = '/home/pi/Pictures'

class CollectImageApp:
    def __init__(self, resolution: Tuple[int, int], fps: int):
        self.resolution = resolution
        self.fps = fps
        
        self.camera = picamera.PiCamera()
        
        self.camera.resolution = self.resolution
        self.camera.framerate = self.fps
        self.camera.rotation = CAMERA_ROTATION
        
        self.frame = np.empty((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        self.process_loop_delay = int(1000 / self.fps)

        self.init_ui()
    
    def init_ui(self):
        self.root = tk.Tk()

        self.root.title('collect_image')
        self.root.geometry(f'{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}')

        self.label = tk.Label(self.root, width=int(self.resolution[0] * 4/5), height=self.resolution[1])
        self.label.pack(side='left')

        self.close_button = tk.Button(self.root, text='Exit', command=self.close)
        self.close_button.pack(expand=True, fill='both', side='right')

        self.capture_button = tk.Button(self.root, text='Capture', command=self.capture_image)
        self.capture_button.pack(expand=True, fill='both', side='right')
    
    def start(self):
        self.label.after(0, self.process_video)
        self.root.mainloop()

    def close(self):
        self.root.destroy()
        self.camera.close()

    def process_video(self):
        self.camera.capture(self.frame, format='bgr', use_video_port=CAMERA_USE_VIDEO_PORT)
        rgba_image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)

        image = Image.fromarray(rgba_image)
        image_tk = ImageTk.PhotoImage(image=image)
        
        self.label.image_tk = image_tk
        self.label.configure(image=image_tk)

        self.label.update_idletasks()
        self.label.after(self.process_loop_delay, self.process_video)

    def capture_image(self):
        time = datetime.datetime.now()
        filename = '{}.jpg'.format(time.strftime('%Y-%m-%d_%H-%M-%S'))
        filepath = os.path.join(IMAGE_SAVE_PATH, filename)

        if cv2.imwrite(filepath, self.frame):
            self.capture_button.configure(bg='green')
        else:
            self.capture_button.configure(bg='red')

if __name__ == '__main__':
    collect_image = CollectImageApp((1280, 720), 30)
    collect_image.start()
