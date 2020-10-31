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


# clean relative path
if [[ "$0" =~ ^. ]]; then
  SCRIPT_PATH="/$(dirname "${0/.\//""}")"
else
  SCRIPT_PATH="/$(dirname "$0")"
fi
SCRIPT_PATH="${SCRIPT_PATH/./""}"

TOOLS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )$SCRIPT_PATH"

# parse arguments
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
  -t|--tools)
    # override TOOLS_DIR with -t|--tools argument value
    TOOLS_DIR="$2"
    shift # past argument
    shift # past value
    ;;
  -h)
    echo "activate.sh help:"
    echo "arguments:"
    echo -e "\t-t|--tools <PATH>\tTools directory path"
    exit 0
    shift
    ;;
esac
done
set -- "${POSITIONAL[@]}"

PROJECT_DIR="$(dirname "$TOOLS_DIR")"
VIRTUALENV_DIR="$PROJECT_DIR/.venv"

activate () {
  # check if virtualenv exist
  if [ -d "$VIRTUALENV_DIR" ]; then
    ACTIVATE_CMD="$VIRTUALENV_DIR/bin/activate"
    # shellcheck source=../.venv/bin/activate
    . "${ACTIVATE_CMD}"
    echo "Activated Python environment: $VIRTUALENV_DIR"
  else
    echo "Python virtual environment does not exist."
    echo "Create it with setup.sh script."
  fi
}

activate
