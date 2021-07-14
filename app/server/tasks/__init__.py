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


from datetime import datetime
from huey import crontab
from io import BytesIO
from os.path import join as join_path
from PIL import Image
from .task_queue import TaskQueue
from ..utils.database.models.alerts import Alert as AlertModel
from ..utils.alerts.email import send_mail


IMAGE_COLLAGE_COLUMNS = 3
IMAGE_COLLAGE_ROWS = 5
IMAGE_COLLAGE_WIDTH = 600
IMAGE_COLLAGE_HEIGHT = 500

task_queue: TaskQueue = TaskQueue()


@task_queue.periodic_task(crontab(minute='*/1'), name='alert')
def send_alerts_task():
    with task_queue.app_db:
        alerts = AlertModel.select().where(AlertModel.delivered == False)
        collage = Image.new(
            'RGB',
            (IMAGE_COLLAGE_COLUMNS*IMAGE_COLLAGE_WIDTH, IMAGE_COLLAGE_ROWS*IMAGE_COLLAGE_HEIGHT),
            color=(255, 255, 255)
        )
        images = []

        image_count = 0
        for alert in alerts:
            if image_count < (IMAGE_COLLAGE_COLUMNS*IMAGE_COLLAGE_ROWS):
                image = Image.open(join_path(
                    task_queue.config.get('STORAGE_SETTINGS').get('DATA_FOLDER'),
                    task_queue.config.get('STORAGE_SETTINGS').get('CAPTURE_FOLDER'),
                    alert.image.image_folder,
                    alert.image.image_file
                ))
                images.append(image.resize((IMAGE_COLLAGE_WIDTH, IMAGE_COLLAGE_HEIGHT)))
            else:
                break
            image_count += 1

        image_count = 0
        for i in range(0, IMAGE_COLLAGE_COLUMNS*IMAGE_COLLAGE_WIDTH, IMAGE_COLLAGE_WIDTH):
            for j in range(0, IMAGE_COLLAGE_ROWS*IMAGE_COLLAGE_HEIGHT, IMAGE_COLLAGE_HEIGHT):
                collage.paste(images[image_count], (i, j))
                image_count += 1

        collage_image = BytesIO()
        collage.save(collage_image, format='JPEG')
        collage_image.seek(0)

        result = {'delivered': False}
        send_mail(
            task_queue.config.get('EMAIL_ALERT_SETTINGS'),
            task_queue.config.get('EMAIL_ALERT_SENDER'),
            task_queue.config.get('EMAIL_ALERT_DESTINATION'),
            task_queue.config.get('EMAIL_ALERT_SUBJECT'),
            {
                'TEXT': 'motion detected',
                'HTML': """\
<html>
  <body>
    <div>motion detected</div>
  </body>
</html>
"""
            },
            collage_image,
            result
        )

        if result['delivered']:
            today = datetime.fromtimestamp(datetime.now().timestamp())
            for alert in alerts:
                alert.delivered = True
                alert.delivery_date = today
                alert.save()