#!/usr/bin/env bash

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


TOOLS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR="$(dirname "$TOOLS_DIR")"
VIRTUALENV_DIR="$PROJECT_DIR/.venv"

# labels
VIRTUALENV_ACTIVATING_LABEL="Activating python virtual environment..."
RUNNING_SERVER_LABEL="Running Server..."
REPLACE_CHAR="="

# check if virtualenv exist
if [ -d "$VIRTUALENV_DIR" ]; then
  # activate virtualenv
  echo -e "\n${VIRTUALENV_ACTIVATING_LABEL}\n${VIRTUALENV_ACTIVATING_LABEL//?/$REPLACE_CHAR}"
  # shellcheck source=./activate.sh
  source ${TOOLS_DIR}/activate.sh -t "$TOOLS_DIR"

  # run server
  echo -e "\n${RUNNING_SERVER_LABEL}\n${RUNNING_SERVER_LABEL//?/$REPLACE_CHAR}"
  cd "$PROJECT_DIR" && python -m "app.server"
else
  echo "Python virtual environment does not exist."
  echo "Create it with setup.sh script."
fi
