#!/usr/bin/env python3
import time
import json
import configparser
import requests
from picamera2 import Picamera2, Preview
from grove.adc import ADC
from datetime import datetime

# --- Load Configuration ---
config = configparser.ConfigParser()
config.read('config.ini')

INTERVAL = float(config['SENSOR']['interval'])  # seconds
THRESHOLD = int(config['SENSOR']['threshold'])  # brightness diff
WIDTH = int(config['CAMERA']['width'])
HEIGHT = int(config['CAMERA']['height'])

# --- Setup Devices ---
adc = ADC(address=0x08)
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={"size": (WIDTH, HEIGHT)})
picam2.configure(camera_config)

# --- Main Loop ---
headers = {
    "Content-Type": "application/json"
}
photo_headers = {
    "Content-Type": "image/jpeg"
}
prev_value = adc.read(0)

while True:
    time.sleep(INTERVAL)
    current_value = adc.read(0)
    print(f"Light sensor: {current_value} (prev: {prev_value})")

    unix_time = int(time.time())
    payload = {
        "timestamp": unix_time,
        "light": current_value,
    }
    try:
        res = requests.post("http://uni.soracom.io", headers=headers, data=json.dumps(payload))
        print(f"POST result: {res.status_code} {res.text}")
        print(f"data: {payload}")
    except Exception as e:
        print(f"Error sending data: {e}")
    if prev_value - current_value >= THRESHOLD:
        filename = f"photo_{unix_time}.jpg"
        local_filename = "photo.jpg"
        picam2.start()
        time.sleep(2)
        picam2.capture_file(local_filename)
        picam2.stop()
        print(f"Photo captured: {filename}")

        try:
            with open(local_filename, "rb") as f:
                requests.post(f"http://harvest-files.soracom.io/please-line-up-the-slippers-dad/{filename}", headers=photo_headers, data=f)
                print(f"Upload result: {res.status_code} {res.text}")
        except Exception as e:
            print(f"Error sending data: {e}")

    prev_value = current_value

