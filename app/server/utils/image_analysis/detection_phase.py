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


import numpy as np
from os.path import join as join_path
from .ml_interpreter import TensorFlowInterpreter


class DetectionPhase:
    entities_allowed = [
        'person',
        'dog',
        'cat'
    ]

    def __init__(self, interpreter: TensorFlowInterpreter):
        self.interpreter = interpreter

    def detect(self, image_data):
        def detection(labels, interpreter):
            interpreter.allocate_tensors()
            threshold = 0.4
            input_details = interpreter.get_input_details()
            input_shape = input_details[0]['shape']
            height = input_shape[1]
            width = input_shape[2]

            self.interpreter.set_input_tensor(interpreter, image_data.copy().convert('RGB').resize((width, height)))
            interpreter.invoke()

            boxes = self.interpreter.get_output_tensor(interpreter, 0)
            classes = self.interpreter.get_output_tensor(interpreter, 1)
            scores = self.interpreter.get_output_tensor(interpreter, 2)
            count = int(self.interpreter.get_output_tensor(interpreter, 3))

            results = []
            for i in range(count):
                if scores[i] >= threshold:
                    ymin, xmin, ymax, xmax = boxes[i]
                    result = {
                        'bounding_box': [ymin * image_data.height, xmin * image_data.width, ymax * image_data.height, xmax * image_data.width],
                        'class_id': labels[classes[i]],
                        'score': scores[i]
                    }

                    if result.get('class_id') in self.entities_allowed:
                        results.append(result)
            return results

        label_file_path = join_path('detection', 'labelmap.txt')
        model_file_path = join_path('detection', 'detect.tflite')
        return self.interpreter.detect_callback(detection, label_file_path, model_file_path)

    def recognize(self, image_data):
        def recognition(interpreter):
            interpreter.allocate_tensors()
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            input_shape = input_details[0]['shape']
            height = input_shape[1]
            width = input_shape[2]

            normalized = image_data.resize((width, height))
            normalized = (np.float32(normalized) - 127.5) / 127.5
            normalized = np.expand_dims(normalized, axis=0)

            interpreter.set_tensor(input_details[0]['index'], normalized)
            interpreter.invoke()

            output_data = interpreter.get_tensor(output_details[0]['index'])
            return np.squeeze(output_data)

        model_file_path = join_path('recognition', 'MobileFaceNet.tflite')
        return self.interpreter.recognize_callback(recognition, model_file_path)
