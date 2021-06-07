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


import argparse
import os
import sys
from subprocess import Popen, PIPE
from sanic import Sanic
from sanic.log import logger
from sanic.response import json
from app.server.utils.database import db_setup
from app.server.modules.capture import capture_module

# get init arguments
argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('--mode', type=str, default='production')
args = argument_parser.parse_args(sys.argv[1:])

# set run mode
environments = ['develop', 'production']
environment = str(args.mode).lower()
if environment not in environments:
    logger.error('Environment \'{}\' not supported'.format(environment))
    exit(1)

# Project Name 'ImgRecSysAlerts', alias for: 'Image Recognition System to Issue Security Alerts'
Server = Sanic('ImgRecSysAlerts')

# load configuration
try:
    Server.update_config('{}/config/{}.py'.format(os.getcwd(), environment))
except FileNotFoundError as e:
    logger.error('!!! the configuration file for \'{}\' does not exist or could not be loaded'.format(environment))

# database setup
Server.__setattr__('DB', db_setup(Server.config))

# register modules
Server.blueprint(capture_module)


@Server.route('/')
async def root(request):
    return json({'home_page': 'TODO'})


@Server.listener('before_server_start')
async def before_server_start(app, loop):
    app.task_queue_process = Popen(['huey_consumer', 'app.server.tasks.task_queue', '-w', '2', '-k', 'process'], stdout=PIPE, stderr=PIPE)
    logger.info('TASK QUEUE STARTED')


@Server.listener('after_server_stop')
async def after_server_stop(app, loop):
    app.task_queue_process.terminate()
    logger.info('TASK QUEUE TERMINATED')


if __name__ == '__main__':
    if Server.config.DEBUG:
        logger.info('DEVELOP MODE ENABLED')

    try:
        Server.run(host=Server.config.HOST, port=Server.config.PORT, debug=Server.config.DEBUG)
    except KeyboardInterrupt:
        Server.stop()
        sys.exit()
