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


from peewee import CharField, ForeignKeyField
from app.server.utils.database.models.images import Recognition
from . import BaseModel


class Person(BaseModel):
    name = CharField(index=True, unique=True)


class Authorized(BaseModel):
    person = ForeignKeyField(Person, backref='authorized', on_delete='SET NULL', null=True, index=True, unique=False)
    recognition = ForeignKeyField(Recognition, backref='authorized', on_delete='CASCADE', index=True, unique=True)
