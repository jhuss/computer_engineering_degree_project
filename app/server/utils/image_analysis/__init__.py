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
from os.path import join as join_path
from PIL import Image, ImageDraw
from queue import Queue
from threading import Thread
from app.server.tasks import TaskQueue
from app.server.utils import NumpyArrayEncoder
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
            # Get the task from the queue and expand the tuple
            task, image_data = self.queue.get()
            try:
                task.call_local(image_data)
            finally:
                self.queue.task_done()


class ImageAnalysis:
    queue = Queue()

    def __init__(self, storage: Storage, task_queue: TaskQueue):
        self.storage = storage
        self.task_queue = task_queue
        self.ml_interpreter = TensorFlowInterpreter(storage)
        self.detection_phase = DetectionPhase(self.ml_interpreter)
        self.image_processing_task = task_queue.task()(self.image_process)
        self.worker = ImageAnalysisWorker(self.queue)
        self.worker.daemon = True
        self.worker.start()

    def add_to_queue(self, images_data):
        for image_data in images_data:
            self.queue.put((self.image_processing_task, image_data))

    def image_process(self, image_data):
        # open and analyze the captured image
        img = Image.open(join_path(self.storage.CAPTURE_PATH, image_data['folder'], image_data['image']))
        image_analyzed = self.detection_phase.detect(img)
        img_edit = io.BytesIO()

        # create db record for results
        analysis_record = None
        image_record = CaptureModel.select().where(
            (CaptureModel.image_file == image_data['image']) & (CaptureModel.image_folder == image_data['folder'])
        ).get()
        try:
            analysis_record = AnalysisModel.get(AnalysisModel.image == image_record.id)
        finally:
            if not analysis_record:
                analysis_record = AnalysisModel()
        analysis_record.image = image_record.id
        analysis_record.analyzed = True
        analysis_record.detected = False

        if len(image_analyzed) > 0:
            analysis_record.detected = True
            analysis_record.analysis_result = json.dumps(image_analyzed, cls=NumpyArrayEncoder)
            analysis_record.save()

            # add shape for detected location
            draw = ImageDraw.Draw(img)
            for obj in image_analyzed:
                ymin, xmin, ymax, xmax = obj['bounding_box']
                xmin = int(xmin * img.width)
                xmax = int(xmax * img.width)
                ymin = int(ymin * img.height)
                ymax = int(ymax * img.height)
                draw.rectangle([xmin, ymin, xmax, ymax], outline=(0xFF, 0, 0, 0xFF))

        # save to DB and return results
        analysis_record.save()
        img.save(img_edit, format='JPEG')
        img_edit.seek(0)
        return {'analysis': image_analyzed, 'image': img_edit.getvalue()}
