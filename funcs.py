import os
import serial
import time
import asyncio

# ==============================================================================
# Get the current weather
# ==============================================================================
get_weather_name = {
    "name": "get_current_weather",
    "description": "Get the current weather in a given location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA",
            },
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["location"],
    },
}

# ==============================================================================
# Light control
# ==============================================================================
light_control_name = {
    "name": "light_control",
    "description": "To turn on or off the light",
    "parameters": {
        "type": "object",
        "properties": {
            "light_mode": {
                "type": "string",
                "description": "1 or 0",
            },
            # "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["light_mode"],
    },
}


def light_control(light_mode):
    arduino_port = '/dev/ttyACM0'
    arduino_baud_rate = 9600
    ser = serial.Serial(arduino_port, arduino_baud_rate, timeout=1)
    time.sleep(2)
    if light_mode == '1':
        ser.write(b'1')
        time.sleep(3)
    elif light_mode == '0':
        ser.write(b'0')
    ser.close()
    return True


# ==============================================================================
# Software control
# ==============================================================================

control_soft_name = {
    "name": "control_soft",
    "description": "open and close software programs, in browser only when they ask open or close",
    "parameters": {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "name of application or web site. Example: instagram, youtube, calendar",
            },
            # "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["app_name"],
    },
}


def control_soft(app_name: str):
    app = app_name.lower()
    print(app)
    match app:
        case "youtube":
            os.system(
                "google-chrome https://youtu.be/VR5oxQ32NGY?si=a2Qc7XaXstumuqNm")
            return True
        case "instagram":
            os.system("google-chrome https://www.instagram.com/")
            return True
        case "calendar":
            os.system("google-chrome https://timetreeapp.com/calendars")
            return True
    return "not done("
