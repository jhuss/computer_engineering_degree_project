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


import os.path
import sqlite3
from peewee import SqliteDatabase
from app.server.utils.database.models.images import Capture, Analysis


def db_setup(conf):
    db_path = os.path.join(conf.get('STORAGE_SETTINGS')['DATA_FOLDER'], conf.get('DATABASE_NAME'))
    db_connection = None
    db_orm = None

    try:
        db_connection = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(e)
    finally:
        if db_connection:
            db_connection.close()
            db_orm = SqliteDatabase(db_path)
            check_tables(db_orm)

    return db_orm


def check_tables(db):
    models = [Capture, Analysis]
    db.bind(models)

    for model in models:
        exist = model.table_exists()
        if not exist:
            model.create_table()
