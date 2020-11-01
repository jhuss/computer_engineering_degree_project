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


# paths
TOOLS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR="$(dirname "$TOOLS_DIR")"
VIRTUALENV_DIR="$PROJECT_DIR/.venv"

# labels
VIRTUALENV_INSTALLING_LABEL="Installing python virtual environment..."
VIRTUALENV_ACTIVATING_LABEL="Activating python virtual environment..."
REQUIREMENTS_INSTALLING_LABEL="Installing python requirements..."
DONE_LABEL="Done"
REPLACE_CHAR="="

# check if virtualenv exist
if [ ! -d "$VIRTUALENV_DIR" ]; then
  echo -e "${VIRTUALENV_INSTALLING_LABEL}\n${VIRTUALENV_INSTALLING_LABEL//?/$REPLACE_CHAR}"
  virtualenv "$VIRTUALENV_DIR" || $(echo "error creating the python virtual environment." && exit 1)

  # activate virtualenv
  echo -e "\n${VIRTUALENV_ACTIVATING_LABEL}\n${VIRTUALENV_ACTIVATING_LABEL//?/$REPLACE_CHAR}"
  # shellcheck source=./activate.sh
  source ${TOOLS_DIR}/activate.sh -t "$TOOLS_DIR"

  echo -e "\n${REQUIREMENTS_INSTALLING_LABEL}\n${REQUIREMENTS_INSTALLING_LABEL//?/$REPLACE_CHAR}"
  pip install -r "$TOOLS_DIR/resources/requirements.txt" || $(echo "error installing requirements." && exit 1)
  echo -e "\n${DONE_LABEL//?/$REPLACE_CHAR}\n${DONE_LABEL}\n${DONE_LABEL//?/$REPLACE_CHAR}"
else
  echo "Python virtual environment already exist."
  echo "Activate it with activate.sh script."
fi
