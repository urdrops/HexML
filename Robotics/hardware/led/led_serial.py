import serial
import time

# Open the serial port (change 'COM3' to your Arduino's port)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Allow some time for the serial connection to establish
flag = True
while flag:
    txt = input("Enter text: ")  # Max value 20 chars
    if txt == "q":
        flag = False
    # Send data to Arduino with a newline character at the end
    data_to_send = f"{txt}\n"
    ser.write(data_to_send.encode())

# Close the serial port
ser.close()
