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


import logging
import os
from huey import SqliteHuey
from huey.consumer_options import ConsumerConfig
from pathlib import Path
from app.server.utils.database import db_setup
from config import develop as dev_env, production as prod_env
from .alerts import register_alert_tasks


environment = os.environ.get('task_queue_environment')
if environment not in ['develop', 'production']:
    print('Environment \'{}\' not supported'.format(environment))
    exit(1)

# load the same config from server
config = dev_env if environment == 'develop' else prod_env
config = config.__dict__


class TaskQueue(SqliteHuey):
    def __init__(self, app_cfg):
        # config db for task queue
        db_folder_path = '{}/{}'.format(app_cfg.get('STORAGE_SETTINGS').get('DATA_FOLDER'), 'task_queue')
        Path(db_folder_path).mkdir(parents=True, exist_ok=True)
        database_path = '{}/{}'.format(db_folder_path, 'tasks.db')

        super().__init__(name='task_queue', filename=database_path)


task_queue = TaskQueue(config)
app_db = db_setup(config)
register_alert_tasks(task_queue, config, app_db)


def task_run():
    import multiprocessing
    multiprocessing.set_start_method('fork')

    # options: '-w 2 -k process'
    consumer_cfg = ConsumerConfig(**{'w': '2', 'k': 'process'})
    consumer_cfg.validate()

    # Set up logging for the "huey" namespace.
    logger = logging.getLogger('huey')
    consumer_cfg.setup_logger(logger)

    consumer = task_queue.create_consumer(**consumer_cfg.values)
    consumer.run()


if __name__ == '__main__':
    task_run()
