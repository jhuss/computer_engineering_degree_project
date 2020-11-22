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
from gpiozero import MotionSensor as GPIOMotionSensor
from sanic.log import logger
from app.server.camera import Camera


class MotionSensor:
    GPIO_PIN: int = 21
    ACTIVITY_THREAD: Optional[threading.Thread] = None
    CAMERA: Optional[Camera] = None

    def __init__(self, camera: Optional[Camera]):
        self.CAMERA = camera
        self.run()

    def sensor_activity(self):
        sensor = GPIOMotionSensor(self.GPIO_PIN)
        sensor.when_motion = self.sensor_on
        sensor.when_no_motion = self.sensor_off
        sigwait([SIGTERM])
        logger.info('Stopping Motion Sensor')

    def sensor_on(self):
        print('SENSOR ON')

    def sensor_off(self):
        print('SENSOR OFF')

    def run(self):
        self.ACTIVITY_THREAD = threading.Thread(target=self.sensor_activity, args=[])
        self.ACTIVITY_THREAD.start()

    def stop(self):
        if self.ACTIVITY_THREAD is not None:
            pthread_kill(self.ACTIVITY_THREAD.ident, SIGTERM)
