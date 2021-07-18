DEBUG = False

# server
SCHEMA = 'http'
PORT = 8000
HOST = 'localhost'
DATABASE_NAME = 'application.db'

# general options
MOTION_SENSOR_ENABLE = True

# camera
CAMERA_SETTINGS = {
    'DEVICES_PATH': '/sys/class/video4linux',
    'PREFERRED_DEVICE': 0,
    'DEVICE_BUFFER': 1,
    'DEVICE_AVOID_GRAB': 3
}

# storage
STORAGE_SETTINGS = {
    'DATA_FOLDER': 'data',
    # relatives to 'DATA_FOLDER'
    'CAPTURE_FOLDER': 'captured_images',
    'ML_MODEL_FOLDER': 'ml_models'
}

# alerts
EMAIL_ALERT_SETTINGS = {
    'SMTP_ADDRESS': '',
    'SMTP_PORT': 25,
    'ACCOUNT_ADDRESS': '',
    'ACCOUNT_PASSWORD': '',
    'STARTTLS': False
}
EMAIL_ALERT_SUBJECT = ''
EMAIL_ALERT_SENDER = ''
EMAIL_ALERT_DESTINATION = ['']
