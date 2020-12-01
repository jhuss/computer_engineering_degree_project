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
from os.path import join as join_path
from pathlib import Path
from datetime import datetime


class StorageSettings(dict):
    DATA_PATH: str = None
    CAPTURE_PATH: str = None


class Storage(object):
    def __init__(self, storage_settings: Optional[StorageSettings]):
        self.DATA_PATH = storage_settings.get('DATA_FOLDER')
        self.CAPTURE_PATH = join_path(self.DATA_PATH, storage_settings.get('CAPTURE_FOLDER'))
        Path(self.CAPTURE_PATH).mkdir(parents=True, exist_ok=True)

    def save_image(self, image, folder_name: str = '', file_name: str = '', file_extension: str = None):
        if file_extension is None or file_extension == '':
            raise AttributeError('the file extension must be specified')

        folder_destination = join_path(self.CAPTURE_PATH, folder_name) if folder_name != '' else self.CAPTURE_PATH
        Path(folder_destination).mkdir(parents=True, exist_ok=True)

        if file_name == '':
            now = datetime.now()
            timestamp = int(now.timestamp())
            file_name = 'captured_{}{}'.format(timestamp, file_extension)
        else:
            file_name = '{}{}'.format(file_name, file_extension)

        image_path = join_path(folder_destination, file_name)
        open(image_path, 'wb').write(image.tobytes())
        return {'folder': folder_destination, 'image': file_name}
