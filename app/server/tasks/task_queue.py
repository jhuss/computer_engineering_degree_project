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


import os
import importlib
from pathlib import Path
from huey import SqliteHuey
from ..utils.database import db_setup


class TaskQueue(SqliteHuey):
    environment = None
    config = None
    app_db = None

    def __init__(self):
        self.environment = os.environ.get('task_queue_environment')

        if self.environment not in ['develop', 'production']:
            print('Environment \'{}\' not supported'.format(self.environment))
            exit(1)

        # load the same config from server
        config_module_name = 'config'
        config_path = '{}/config/{}.py'.format(os.getcwd(), self.environment)
        spec = importlib.util.spec_from_file_location(config_module_name, config_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.config = module.__dict__

        # config db for task queue
        db_folder_path = '{}/{}'.format(self.config.get('STORAGE_SETTINGS').get('DATA_FOLDER'), 'task_queue')
        Path(db_folder_path).mkdir(parents=True, exist_ok=True)
        database_path = '{}/{}'.format(db_folder_path, 'tasks.db')

        # APP db
        self.app_db = db_setup(self.config)

        super().__init__(name='task_queue', filename=database_path)
