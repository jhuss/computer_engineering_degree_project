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


from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl


def send_mail(smtp_config, sender, destination, subject, body, collage_image, result):
    context = ssl.create_default_context()
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(destination)
    message.attach(MIMEText(body.get('TEXT', ''), 'plain'))
    message.attach(MIMEText(body.get('HTML', ''), 'html'))
    img = MIMEImage(collage_image.getvalue())
    img.add_header('Content-Disposition', 'attachment', filename='motion_detected.jpg')
    message.attach(img)

    try:
        server = smtplib.SMTP(smtp_config.get('SMTP_ADDRESS'), smtp_config.get('SMTP_PORT'))
        with server:
            if smtp_config.get('STARTTLS', False):
                server.starttls(context=context)
            server.login(smtp_config.get('ACCOUNT_ADDRESS'), smtp_config.get('ACCOUNT_PASSWORD'))
            server.sendmail(
                smtp_config.get('ACCOUNT_ADDRESS'), destination, message.as_string()
            )
            result['delivered'] = True
    except Exception as e:
        print(e)
