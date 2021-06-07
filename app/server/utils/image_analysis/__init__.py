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


import io
import json
from PIL import Image, ImageDraw
from queue import Queue
from threading import Thread
from app.server.utils import NumpyArrayEncoder
from app.server.utils.alerts import create_alert
from app.server.utils.storage import Storage
from app.server.utils.database.models.images import Capture as CaptureModel, Analysis as AnalysisModel
from .ml_interpreter import TensorFlowInterpreter
from .detection_phase import DetectionPhase


class ImageAnalysisWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the task from the queue and execute
            task, image_data = self.queue.get()
            try:
                task(image_data)
            finally:
                self.queue.task_done()


class ImageAnalysis:
    queue = Queue()

    def __init__(self, storage: Storage):
        self.storage = storage
        self.ml_interpreter = TensorFlowInterpreter(storage)
        self.detection_phase = DetectionPhase(self.ml_interpreter)
        self.worker = ImageAnalysisWorker(self.queue)
        self.worker.daemon = True
        self.worker.start()

    def add_to_queue(self, images_data):
        for image_data in images_data:
            self.queue.put((self.image_process, image_data))

    def image_process(self, image_data):
        image_analyzed = self.detection_phase.detect(Image.open(image_data['binary']))

        # create db record for results
        image_record = CaptureModel.select().where(
            (CaptureModel.image_file == image_data['image']) & (CaptureModel.image_folder == image_data['folder'])
        ).get()
        analysis_record, created = AnalysisModel.get_or_create(
            image=image_record,
            defaults={
                'analyzed': True,
                'detected': True
            }
        )

        if len(image_analyzed) > 0:
            analysis_record.detected = True
            analysis_record.analysis_result = json.dumps(image_analyzed, cls=NumpyArrayEncoder)
            analysis_record.save()
            create_alert(image_record, analysis_record)

        return image_analyzed

    def draw_detected_area(self, image, analysis_result):
        pil_image = Image.open(image)
        image_edit = io.BytesIO()

        # add shape for detected location
        draw = ImageDraw.Draw(pil_image)
        for obj in analysis_result:
            ymin, xmin, ymax, xmax = obj['bounding_box']
            xmin = int(xmin * pil_image.width)
            xmax = int(xmax * pil_image.width)
            ymin = int(ymin * pil_image.height)
            ymax = int(ymax * pil_image.height)
            draw.rectangle([xmin, ymin, xmax, ymax], outline=(0xFF, 0, 0, 0xFF))
        pil_image.save(image_edit, format='JPEG')
        image_edit.seek(0)

        return image_edit
