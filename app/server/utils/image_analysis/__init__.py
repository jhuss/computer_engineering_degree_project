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


from os.path import join as join_path
from PIL import Image
from queue import Queue
from threading import Thread
from app.server.tasks import task_queue
from app.server.utils.storage import Storage
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

    def __init__(self, storage: Storage):
        self.storage = storage
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
        # image_data example: {'folder': 'data/captured_images', 'image': 'capture_16:12:2020_04:02:27.jpg'}
        img = Image.open(join_path(image_data['folder'], image_data['image']))
        image_analyzed = self.detection_phase.detect(img)
        # TODO: create alert if image_analyzed has results
