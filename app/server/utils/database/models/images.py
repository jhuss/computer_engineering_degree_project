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


from peewee import ForeignKeyField, CharField, BooleanField, DateTimeField, BlobField
from . import BaseModel


class Capture(BaseModel):
    image_file = CharField(index=True, unique=False)
    image_folder = CharField(index=True, unique=False)
    datetime = DateTimeField()


class Analysis(BaseModel):
    image = ForeignKeyField(Capture, backref='analysis', on_delete='CASCADE', unique=True)
    analyzed = BooleanField(default=False)
    detected = BooleanField(default=False)
    recognized = BooleanField(default=False)
    analysis_result = CharField(null=True)


class Recognition(BaseModel):
    analysis = ForeignKeyField(Analysis, backref='recognition', on_delete='CASCADE', index=True, unique=False)
    face_box = CharField(null=False)
    result = BlobField(null=False, index=True, unique=True)
