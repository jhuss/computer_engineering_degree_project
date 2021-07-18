import logging
import os
from huey import SqliteHuey
from huey.consumer_options import ConsumerConfig
from pathlib import Path
from app.server.utils.database import db_setup
from config import develop as dev_env, production as prod_env
from .alerts import register_alert_tasks


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
        self.config = dev_env if self.environment == 'develop' else prod_env
        self.config = self.config.__dict__

        # config db for task queue
        db_folder_path = '{}/{}'.format(self.config.get('STORAGE_SETTINGS').get('DATA_FOLDER'), 'task_queue')
        Path(db_folder_path).mkdir(parents=True, exist_ok=True)
        database_path = '{}/{}'.format(db_folder_path, 'tasks.db')

        # APP db
        self.app_db = db_setup(self.config)

        super().__init__(name='task_queue', filename=database_path)


task_queue = TaskQueue()
register_alert_tasks(task_queue)


def task_run():
    import multiprocessing
    multiprocessing.set_start_method('fork')

    # options: '-w 2 -k process'
    config = ConsumerConfig(**{'w': '2', 'k': 'process'})
    config.validate()

    # Set up logging for the "huey" namespace.
    logger = logging.getLogger('huey')
    config.setup_logger(logger)

    consumer = task_queue.create_consumer(**config.values)
    consumer.run()


if __name__ == '__main__':
    task_run()
