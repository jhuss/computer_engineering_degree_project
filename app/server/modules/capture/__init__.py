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
from sanic.response import json, raw
from sanic import Blueprint
from app.server.camera import Camera

capture_module = Blueprint('capture_module')
config: dict = {}
camera: Optional[Camera] = None


@capture_module.listener('before_server_start')
async def setup_capture(app, loop):
    global config
    global camera

    config = app.config
    camera = Camera(config.get('CAMERA_SETTINGS'))


@capture_module.route('/capture', methods=['GET'])
async def capture(request):
    captured_image = camera.get_image()

    if captured_image is not None:
        return raw(captured_image.tobytes(), content_type="image/png")
    else:
        return json({"error": "device not found"}, 500)
