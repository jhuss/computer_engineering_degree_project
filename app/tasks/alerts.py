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
import math
from os.path import join as join_path
from PIL import Image
from app.server.utils.database.models.alerts import Alert as AlertModel
from app.server.utils.alerts.email import send_mail


MAX_IMAGE_COLLAGE_COLUMNS = 3
MAX_IMAGE_COLLAGE_ROWS = 5
IMAGE_COLLAGE_WIDTH = 600
IMAGE_COLLAGE_HEIGHT = 500


def register_alert_tasks(task_queue, app_cfg, app_db):
    @task_queue.periodic_task(crontab(minute='*/1'), name='alert')
    def send_alerts_task():
        with app_db:
            alerts = AlertModel.select().where(AlertModel.delivered == False)
            images = []
            image_folders = []
            image_count = 0

            for alert in alerts:
                image_folder = alert.image.image_folder
                if image_folder == '':
                    image_folder = 'ungrouped'
                image_folders.append(image_folder)

                if image_count < (MAX_IMAGE_COLLAGE_COLUMNS * MAX_IMAGE_COLLAGE_ROWS):
                    image = Image.open(join_path(
                        app_cfg.get('STORAGE_SETTINGS').get('DATA_FOLDER'),
                        app_cfg.get('STORAGE_SETTINGS').get('CAPTURE_FOLDER'),
                        alert.image.image_folder,
                        alert.image.image_file
                    ))
                    images.append(image.resize((IMAGE_COLLAGE_WIDTH, IMAGE_COLLAGE_HEIGHT)))
                else:
                    break
                image_count += 1

            if image_count > 0:
                image_count = 0
                image_length = len(images)
                collage_columns = image_length if image_length < MAX_IMAGE_COLLAGE_COLUMNS else MAX_IMAGE_COLLAGE_COLUMNS
                collage_rows = 1 if image_length <= MAX_IMAGE_COLLAGE_COLUMNS else math.ceil(image_length/MAX_IMAGE_COLLAGE_COLUMNS)
                collage = Image.new(
                    'RGB',
                    (collage_columns * IMAGE_COLLAGE_WIDTH, collage_rows * IMAGE_COLLAGE_HEIGHT),
                    color=(255, 255, 255)
                )

                for i in range(0, collage_rows * IMAGE_COLLAGE_HEIGHT, IMAGE_COLLAGE_HEIGHT):
                    for j in range(0, collage_columns * IMAGE_COLLAGE_WIDTH, IMAGE_COLLAGE_WIDTH):
                        if image_count < image_length:
                            collage.paste(images[image_count], (j, i))
                            image_count += 1

                collage_image = BytesIO()
                collage.save(collage_image, format='JPEG')
                collage_image.seek(0)

                email_body = {
                    'TEXT': 'Security Alerts\nReports:\n{0}',
                    'HTML': """\
<html>
  <body>
    <div><h3>Security Alert</h3></div>
    <div><strong>Reports:</strong></div>
    <div>{0}</div>
  </body>
</html>
"""
                }

                report_links = []
                for folder in image_folders:
                    report_links.append('{0}://{1}:{2}/reports/{3}'.format(
                        app_cfg.get('SCHEMA'),
                        app_cfg.get('HOST'),
                        app_cfg.get('PORT'),
                        folder
                    ))
                email_body['TEXT'] = email_body['TEXT'].format('\n'.join(report_links))
                email_body['HTML'] = email_body['HTML'].format('\n'.join(list(map(lambda x: '<a href="{0}">VIEW REPORT</a>'.format(x), report_links))))

                result = {'delivered': False}
                send_mail(
                    app_cfg.get('EMAIL_ALERT_SETTINGS'),
                    app_cfg.get('EMAIL_ALERT_SENDER'),
                    app_cfg.get('EMAIL_ALERT_DESTINATION'),
                    app_cfg.get('EMAIL_ALERT_SUBJECT'),
                    email_body,
                    collage_image,
                    result
                )

                if result['delivered']:
                    today = datetime.fromtimestamp(datetime.now().timestamp())
                    for alert in alerts:
                        alert.delivered = True
                        alert.delivery_date = today
                        alert.save()
