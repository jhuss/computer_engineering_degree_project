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


from app.server.utils.database.models.alerts import Alert as AlertModel


def create_alert(image_record, analysis_record, authorized_records):
    all_persons = list(map(lambda x: x.person if x.person is not None else None, authorized_records))

    if len(all_persons) == 0 or None in all_persons:
        alert_record, created = AlertModel.get_or_create(
            image=image_record,
            analysis=analysis_record,
            delivery_method=AlertModel.DeliveryChoices.EMAIL
        )
        return alert_record
