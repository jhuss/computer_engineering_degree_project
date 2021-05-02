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
from enum import Enum
from peewee import ForeignKeyField, BooleanField, DateTimeField
from app.server.utils.database.models.images import Capture, Analysis
from . import BaseModel, EnumField


class Alert(BaseModel):
    class DeliveryChoices(Enum):
        EMAIL = 1
        SMS = 2  # to implement

    image = ForeignKeyField(Capture, backref='alert', unique=False)
    analysis = ForeignKeyField(Analysis, backref='alert', unique=False)
    delivery_method = EnumField(choices=DeliveryChoices)
    delivered = BooleanField(default=False)
    viewed_alert = BooleanField(default=False)
    create_date = DateTimeField(default=datetime.fromtimestamp(datetime.now().timestamp()))
    delivery_date = DateTimeField(null=True)
    viewed_date = DateTimeField(null=True)
