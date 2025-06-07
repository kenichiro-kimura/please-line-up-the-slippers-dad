#!/usr/bin/env python3
import time
import json
import configparser
import requests
from picamera import PiCamera
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
camera = PiCamera()
camera.resolution = (WIDTH, HEIGHT)

# --- Main Loop ---
prev_value = adc.read(0)

while True:
    time.sleep(INTERVAL)
    current_value = adc.read(0)
    print(f"Light sensor: {current_value} (prev: {prev_value})")

    if prev_value - current_value >= THRESHOLD:
        unix_time = int(time.time())
        filename = f"photo_{unix_time}.jpg"
        camera.start_preview()
        time.sleep(2)
        camera.capture(filename)
        camera.stop_preview()
        print(f"Photo captured: {filename}")

        payload = {
            "timestamp": unix_time,
            "light": current_value,
            "image": filename
        }

        try:
            with open(filename, "rb") as f:
                requests.post("http://uni.soracom.io", files={
                    "file": (filename, f, "image/jpeg")
                })
        except Exception as e:
            print(f"Error sending data: {e}")

    prev_value = current_value

