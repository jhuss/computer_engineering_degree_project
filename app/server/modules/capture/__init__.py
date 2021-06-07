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


from datetime import datetime
import io
from typing import Optional
from sanic import Blueprint
from sanic.response import json, raw
from sanic.log import logger
from app.server.utils.camera import Camera
from app.server.utils.storage import Storage
from app.server.utils.database.models.images import Capture as CaptureModel
from app.server.utils.image_analysis import ImageAnalysis
from .motion_sensor import MotionSensor

capture_module = Blueprint('capture_module')
config: dict = {}
camera: Optional[Camera] = None
storage: Optional[Storage] = None
image_analysis: Optional[ImageAnalysis] = None
motion_capture: Optional[MotionSensor] = None


@capture_module.listener('before_server_start')
async def setup_capture(app, loop):
    global config
    global camera
    global storage
    global image_analysis
    global motion_capture

    config = app.config
    camera = Camera(config.get('CAMERA_SETTINGS'))
    storage = Storage(config.get('STORAGE_SETTINGS'))
    image_analysis = ImageAnalysis(storage)

    logger.info('MOTION SENSOR ENABLED: {}'.format(config.get('MOTION_SENSOR_ENABLE')))
    if config.get('MOTION_SENSOR_ENABLE') is True:
        motion_capture = MotionSensor(camera, storage, image_analysis)


@capture_module.listener('before_server_stop')
async def stop_capture(app, loop):
    if motion_capture is not None:
        motion_capture.stop()


@capture_module.route('/capture', methods=['GET'])
async def capture(request):
    captured_image = camera.get_image()

    if captured_image is not None:
        saved_image = storage.save_image(
            captured_image,
            '',
            'capture_{}'.format(datetime.now().strftime("%d:%m:%Y_%H:%M:%S")),
            camera.IMAGE_EXTENSION
        )
        saved_image['binary'] = io.BytesIO(captured_image.tobytes())

        # add DB record of captured image
        CaptureModel.insert(
            image_file=saved_image.get('image'),
            image_folder=saved_image.get('folder'),
            datetime=datetime.fromtimestamp(saved_image.get('timestamp'))
        ).execute()

        result = image_analysis.image_process(saved_image)
        if len(result) > 0:
            captured_image = image_analysis.draw_detected_area(saved_image["binary"], result)

        return raw(captured_image.getvalue(), content_type='image/jpeg')
    else:
        return json({'error': 'device not found'}, 500)
