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
from peewee import fn
from sanic import Blueprint
from sanic.response import raw
from typing import Optional
from app.server import jinja
from app.server.utils.database.models.images import Capture as CaptureModel
from app.server.utils.storage import Storage
import math


alert_module = Blueprint('alert_module', url_prefix='reports')
config: dict = {}
storage: Optional[Storage] = None


@alert_module.listener('before_server_start')
async def setup_alert(app, loop):
    global config
    global storage
    config = app.config
    storage = Storage(config.get('STORAGE_SETTINGS'))


@alert_module.route('/', methods=['GET'])
async def alert_reports(request):
    context = {
        'title': '{}: Reports'.format(request.app.name),
        'data': {
            'reports': []
        }
    }

    reports = CaptureModel.select(
        CaptureModel.image_folder,
        fn.COUNT(CaptureModel.image_file).alias('images'),
        fn.MIN(CaptureModel.datetime).alias('start'),
        fn.MAX(CaptureModel.datetime).alias('end')
    ).group_by(CaptureModel.image_folder).dicts()

    for report in reports:
        if report['image_folder'] != '':
            context['data']['reports'].append({
                'images_count': report['images'],
                'date_start': report['start'].strftime('%d/%m/%Y (%H:%M:%S)'),
                'date_end': report['end'].strftime('%d/%m/%Y (%H:%M:%S)'),
                'report_url': request.app.url_for('alert_module.alert_report_details', group=report['image_folder'])
            })

    return jinja.render('reports.jinja2', request, context=context)


@alert_module.route('/<group:string>', methods=['GET'])
async def alert_report_details(request, group):
    context = {
        'title': '{}: Report details'.format(request.app.name),
        'data': {
            'group': group,
            'images': [],
            'pagination': []
        }
    }
    args = request.get_args()

    images_per_page = 10
    current_page = int(args.get('page', default=1))
    if current_page <= 0:
        current_page = 1
    context['data']['current_page'] = current_page

    report_details = CaptureModel.select(
        CaptureModel.image_file,
        CaptureModel.datetime,
    ).where(CaptureModel.image_folder == group).paginate(current_page, images_per_page).dicts()

    for detail in report_details:
        context['data']['images'].append({
            'image_file': detail['image_file'],
            'datetime': detail['datetime'].strftime('%d/%m/%Y (%H:%M:%S)')
        })

    records = CaptureModel.select().where(CaptureModel.image_folder == group).count()
    for page in list(range(1, (math.ceil(records / images_per_page) + 1))):
        context['data']['pagination'].append({
            'number': page,
            'url': request.app.url_for('alert_module.alert_report_details', group=group, page=page)
        })

    return jinja.render('report_detail.jinja2', request, context=context)


@alert_module.route('/captured_image', methods=['GET'])
async def captured_image(request):
    args = request.get_args()
    image_folder = args.get('folder', default='')
    image_name = args.get('image')
    image = open(join_path(storage.CAPTURE_PATH, image_folder, image_name), 'rb')
    return raw(image.read(), content_type='image/jpeg')
