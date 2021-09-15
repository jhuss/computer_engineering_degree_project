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


import cv2 as cv
import io
import json
from mtcnn_cv2 import MTCNN
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from queue import Queue
from threading import Thread
from app.server.utils import NumpyArrayEncoder
from app.server.utils.alerts import create_alert
from app.server.utils.storage import Storage
from app.server.utils.database.models.images import Capture as CaptureModel, Analysis as AnalysisModel, Recognition as RecognitionModel
from app.server.utils.database.models.authorized import Authorized as AuthorizedModel
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
        self.face_detector = MTCNN()
        self.detection_phase = DetectionPhase(self.ml_interpreter)
        self.worker = ImageAnalysisWorker(self.queue)
        self.worker.daemon = True
        self.worker.start()

    def add_to_queue(self, images_data):
        for image_data in images_data:
            self.queue.put((self.image_process, image_data))

    def image_process(self, image_data):
        # create db record for results
        image_record = CaptureModel.select().where(
            (CaptureModel.image_file == image_data['image']) & (CaptureModel.image_folder == image_data['folder'])
        ).get()
        analysis_record, created = AnalysisModel.get_or_create(
            image=image_record,
            defaults={
                'analyzed': True,
                'detected': False
            }
        )

        # find persons in the image
        raw_image = Image.open(image_data['binary'])
        image_analyzed = self.detection_phase.detect(raw_image)

        if len(image_analyzed) > 0:
            analysis_record.detected = True
            analysis_record.analysis_result = json.dumps(image_analyzed, cls=NumpyArrayEncoder)
            analysis_record.save()

        # find faces in the image
        image_array = cv.cvtColor(np.array(raw_image), cv.COLOR_BGR2RGB)
        faces_info = self.face_detector.detect_faces(image_array)
        authorized_found = []

        if len(faces_info) > 0:
            # store each face detected
            for face_info in faces_info:
                [X, Y, W, H] = face_info['box']
                recognized_image = self.detection_phase.recognize(Image.fromarray(image_array[Y:Y+H, X:X+W]))

                recognized_binary = io.BytesIO()
                np.save(recognized_binary, recognized_image)
                recognized_binary.seek(0)

                recognition_record, created = RecognitionModel.get_or_create(
                    analysis=analysis_record,
                    defaults={
                        'face_box': json.dumps(face_info['box']),
                        'result': recognized_binary.read()
                    }
                )
                authorized = AuthorizedModel.get_or_none(recognition=recognition_record)

                if not authorized:
                    all_authorized = AuthorizedModel.select()
                    authorized_matched = None

                    for authorized in all_authorized.objects():
                        stored_recognition = io.BytesIO(authorized.recognition.result)
                        stored_recognition.seek(0)
                        stored_recognition = np.load(stored_recognition, allow_pickle=True)

                        # calculate distance
                        distance = round(cv.norm(recognized_image, stored_recognition), 3)
                        if distance <= 0.799:
                            authorized_matched = authorized
                            break

                    new_authorized, created = AuthorizedModel.get_or_create(
                        person=authorized_matched.person if authorized_matched else None,
                        recognition=recognition_record
                    )
                    authorized_found.append(new_authorized)
                else:
                    authorized_found.append(authorized)

            analysis_record.recognized = True
            analysis_record.save()

        create_alert(image_record, analysis_record, authorized_found)
        return image_analyzed, authorized_found

    def draw_detected_area(self, image, analysis_result, authorized=None):
        pil_image = Image.open(image)
        image_edit = io.BytesIO()
        if authorized is None:
            authorized = []

        # add shape for detected location
        draw = ImageDraw.Draw(pil_image)
        for obj in analysis_result:
            ymin, xmin, ymax, xmax = obj['bounding_box']
            draw.rectangle([xmin, ymin, xmax, ymax], outline=(0xFF, 0, 0, 0xFF))

        for auth in authorized:
            xmin, ymin, xmax, ymax = json.loads(auth.recognition.face_box)
            draw.rectangle([xmin, ymin, xmin+xmax, ymin+ymax], outline=(0xFF, 0, 0, 0xFF))

            font = ImageFont.truetype("DejaVuSerif", size=12)
            text = '{}'.format('unknown {}'.format(auth.id) if not auth.person else auth.person.name)
            text_size = font.getsize(text)
            box = Image.new('RGBA', (text_size[0]+5, text_size[1]+5), "red")
            tex_box = ImageDraw.Draw(box)
            tex_box.text((3, 0), text, font=font)
            pil_image.paste(box, (xmin, ymin+ymax))

        pil_image.save(image_edit, format='JPEG')
        image_edit.seek(0)

        return image_edit
