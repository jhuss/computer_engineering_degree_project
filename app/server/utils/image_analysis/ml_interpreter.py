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
import re
from tflite_runtime.interpreter import Interpreter
from app.server.utils.storage import Storage


class TensorFlowInterpreter:
    def __init__(self, storage: Storage):
        self.storage = storage

    def load_labels(self, path):
        with open(join_path(self.storage.ML_MODEL_PATH, path), 'r', encoding='utf-8') as f:
            lines = f.readlines()
            labels = {}
            for row_number, content in enumerate(lines):
                pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
                if len(pair) == 2 and pair[0].strip().isdigit():
                    labels[int(pair[0])] = pair[1].strip()
                else:
                    labels[row_number] = pair[0].strip()
        return labels

    def set_input_tensor(self, interpreter, image):
        tensor_index = interpreter.get_input_details()[0]['index']
        input_tensor = interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image

    def get_output_tensor(self, interpreter, index):
        output_details = interpreter.get_output_details()[index]
        tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
        return tensor

    def detect_callback(self, callback, label_file_path, model_file_path):
        return callback(self.load_labels(label_file_path), Interpreter(join_path(self.storage.ML_MODEL_PATH, model_file_path)))

    def recognize_callback(self, callback, model_file_path):
        return callback(Interpreter(join_path(self.storage.ML_MODEL_PATH, model_file_path)))
