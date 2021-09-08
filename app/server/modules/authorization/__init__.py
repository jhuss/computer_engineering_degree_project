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


from sanic import Blueprint, response
from app.server.utils.database.models.authorized import Person as PersonModel, Authorized as AuthorizedModel


authorization_module = Blueprint('authorization_module')


@authorization_module.route('/authorized', methods=['GET'])
async def authorized(request):
    available_person = []
    for person in PersonModel.select():
        available_person.append(person.name)
    available_person.append('Other')
    return response.json(available_person)


@authorization_module.route('/update_authorized', methods=['POST'])
async def update_authorized(request):
    values = request.json
    return_error = False
    return_msg = 'unprocessed'

    if 'record' in values and 'name' in values:
        authorized_id = int(values['record'])
        new_name = str(values['name'])

        authorized_record = AuthorizedModel.get_or_none(id=authorized_id)
        if authorized_record:
            person = None
            if len(new_name) > 0:
                person, created = PersonModel.get_or_create(name=new_name)
            authorized_record.person = person
            authorized_record.save()
            return_msg = 'updated'
        else:
            return_error = True
            return_msg = 'record doesn\'t exist'

    return response.json({'received': True, 'message': return_msg}, status=200 if not return_error else 400)
