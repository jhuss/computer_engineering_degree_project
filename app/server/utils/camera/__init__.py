#   Copyright 2020 Jesus Jerez <https://jerez.link>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from typing import Optional, Callable
import cv2 as cv
import os
import re
from time import sleep
import threading
from .suppress_output import SuppressOutput


class CameraSettings(dict):
    DEVICES_PATH: str = None
    PREFERRED_DEVICE: int = None
    DEVICE_BUFFER: int = None
    DEVICE_AVOID_GRAB: int = None


class Camera:
    API_CONTROL: int = cv.CAP_V4L2
    IMAGE_EXTENSION: str = '.jpg'
    ENCODE_PARAMETERS: list = [int(cv.IMWRITE_JPEG_QUALITY), 85]
    FRAMES_PER_SECOND: int = 16

    def __init__(self, camera_settings: Optional[CameraSettings]):
        self.DEVICES_PATH = camera_settings.get('DEVICES_PATH')
        self.PREFERRED_DEVICE = camera_settings.get('PREFERRED_DEVICE')
        self.DEVICE_BUFFER = camera_settings.get('DEVICE_BUFFER')
        self.DEVICE_AVOID_GRAB = camera_settings.get('DEVICE_AVOID_GRAB')
        self.AVAILABLE_DEVICES = self.get_available_devices()

    def get_device(self, index):
        camera_info = None

        with SuppressOutput():
            try:
                camera_device = cv.VideoCapture(index, self.API_CONTROL)

                if camera_device.isOpened():
                    camera_info = camera_device
                    # TODO: move to config
                    width = 1280
                    height = 960
                    camera_info.set(cv.CAP_PROP_FRAME_WIDTH, width)
                    camera_info.set(cv.CAP_PROP_FRAME_HEIGHT, height)
                    camera_info.set(cv.CAP_PROP_AUTOFOCUS, False)
                    camera_info.set(cv.CAP_PROP_BUFFERSIZE, self.DEVICE_BUFFER)
            except Exception as e:
                pass

        return camera_info

    def get_available_devices(self):
        devices = []
        os_devices = os.listdir(self.DEVICES_PATH)

        for os_device in os_devices:
            device_idx = int(re.match('.*?([0-9]+)$', os_device).group(1))
            device = self.get_device(device_idx)

            if device:
                devices.append({'name': os_device, 'idx': device_idx, 'control': device})
                device.grab()

        return sorted(devices, key=lambda i: i['idx'])

    def get_from_available_devices(self, device_idx: int):
        try:
            return next(iter(list(filter(lambda x: x.get('idx') == device_idx, self.AVAILABLE_DEVICES))))
        except Exception as e:
            print(e)
            return None

    def get_device_control(self, device_idx: int):
        device_idx = device_idx if device_idx is not None else self.PREFERRED_DEVICE
        device = self.get_from_available_devices(device_idx)

        if device is None:
            return None

        return device.get('control')

    def get_image(self, device_idx: int = None):
        device_control = self.get_device_control(device_idx)
        grab = None
        frame = None

        if device_control is not None:
            for i in range(self.DEVICE_AVOID_GRAB):
                grab = device_control.grab()  # avoid buffer

            _, frame = device_control.retrieve(grab)
            _, frame = cv.imencode(self.IMAGE_EXTENSION, cv.rotate(frame, cv.ROTATE_180), self.ENCODE_PARAMETERS)

        return frame

    def continuous_capture_thread(self, event_control: threading.Event, capture_callback: Callable[[list, int], None] = None, device_idx: int = None):
        device_control = self.get_device_control(device_idx)

        if device_control is not None:
            global_frames_count = 0

            for i in range(self.DEVICE_AVOID_GRAB):
                device_control.grab()  # avoid buffer

            while not event_control.isSet():
                frame_counter = 0
                frame_time = float(1/self.FRAMES_PER_SECOND)

                while frame_counter < self.FRAMES_PER_SECOND:
                    frame_counter += 1
                    global_frames_count += 1
                    grab = device_control.grab()
                    _, frame = device_control.retrieve(grab)
                    _, frame = cv.imencode(self.IMAGE_EXTENSION, cv.rotate(frame, cv.ROTATE_180), self.ENCODE_PARAMETERS)
                    if frame is not None and capture_callback is not None:
                        capture_callback(frame, global_frames_count)
                    else:
                        print('--CAPTURE ERROR--')

                    # check if the sensor turns off while taking photos
                    if event_control.isSet():
                        break

                    sleep(frame_time)
