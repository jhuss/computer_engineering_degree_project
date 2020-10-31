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


from sanic import Sanic
from sanic.response import json

# Project Name "ImgRecSysAlerts", alias for: "Image Recognition System to Issue Security Alerts"
Server = Sanic("ImgRecSysAlerts")


@Server.route("/")
async def test(request):
    return json({"hello": "world"})

if __name__ == "__main__":
    Server.run(host="0.0.0.0", port=8000)
