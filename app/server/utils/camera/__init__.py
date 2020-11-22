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


from typing import Optional
import cv2 as cv
import os
import re
from .suppress_output import SuppressOutput


class CameraSettings(dict):
    DEVICES_PATH: str = None
    PREFERRED_DEVICE: int = None
    DEVICE_BUFFER: int = None
    DEVICE_AVOID_GRAB: int = None


class Camera:
    API_CONTROL = cv.CAP_V4L2

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

    def get_image_from(self, device_idx: int):
        try:
            device = next(iter(list(filter(lambda x: x.get('idx') == device_idx, self.AVAILABLE_DEVICES))))
            device_control = device.get('control')

            grab = None
            for i in range(self.DEVICE_AVOID_GRAB):
                grab = device_control.grab()  # avoid buffer
            _, frame = device_control.retrieve(grab)
            _, frame = cv.imencode('.png', cv.rotate(frame, cv.ROTATE_180))

            return frame
        except Exception as e:
            print(e)
            return None

    def get_image(self):
        return self.get_image_from(self.PREFERRED_DEVICE)
