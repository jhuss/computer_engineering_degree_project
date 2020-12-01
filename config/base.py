DEBUG = False

# server
PORT = 8000
HOST = 'localhost'

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
    'CAPTURE_FOLDER': 'captured_images'  # relatives to DATA_FOLDER
}
