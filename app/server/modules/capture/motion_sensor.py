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
import threading
from signal import SIGTERM, sigwait, pthread_kill
from datetime import datetime
from uuid import uuid4
from gpiozero import MotionSensor as GPIOMotionSensor
from sanic.log import logger
from app.server.utils.camera import Camera
from app.server.utils.storage import Storage
from app.server.utils.image_analysis import ImageAnalysis


class MotionSensor:
    GPIO_PIN: int = 21
    ACTIVITY_THREAD: Optional[threading.Thread] = None
    CAPTURE_THREAD_EVENT: Optional[threading.Event] = None
    CAPTURE_THREAD: Optional[threading.Thread] = None
    CAMERA: Optional[Camera] = None
    STORAGE: Optional[Storage] = None
    IMAGE_ANALYSIS: Optional[ImageAnalysis] = None
    SENSOR_ACTIVATION_ID: str = None

    def __init__(self, camera: Camera, storage: Storage, image_analysis: ImageAnalysis):
        self.CAMERA = camera
        self.STORAGE = storage
        self.IMAGE_ANALYSIS = image_analysis
        self.run()

    def sensor_activity(self):
        sensor = GPIOMotionSensor(self.GPIO_PIN)
        sensor.when_motion = self.sensor_on
        sensor.when_no_motion = self.sensor_off
        sigwait([SIGTERM])
        logger.info('Stopping Motion Sensor')

    def sensor_on(self):
        logger.info('SENSOR ACTIVATED!')

        now = datetime.now()
        timestamp = int(now.timestamp())
        self.SENSOR_ACTIVATION_ID = '{}_{}'.format(timestamp, str(uuid4()))

        self.CAPTURE_THREAD_EVENT = threading.Event()
        self.CAPTURE_THREAD = threading.Thread(
            target=self.CAMERA.continuous_capture_thread,
            args=[self.CAPTURE_THREAD_EVENT, self.continuous_capture_callback]
        )
        self.CAPTURE_THREAD.start()

    def continuous_capture_callback(self, frame, frames_count):
        saved_image = self.STORAGE.save_image(
            frame,
            self.SENSOR_ACTIVATION_ID,
            'capture_{}'.format(frames_count),
            self.CAMERA.IMAGE_EXTENSION
        )
        self.IMAGE_ANALYSIS.add_to_queue([saved_image])

    def sensor_off(self):
        logger.info('SENSOR QUIET')

        if self.CAPTURE_THREAD_EVENT:
            self.CAPTURE_THREAD_EVENT.set()
            self.CAPTURE_THREAD.join()

    def run(self):
        self.ACTIVITY_THREAD = threading.Thread(target=self.sensor_activity, args=[])
        self.ACTIVITY_THREAD.start()

    def stop(self):
        if self.ACTIVITY_THREAD is not None:
            pthread_kill(self.ACTIVITY_THREAD.ident, SIGTERM)
