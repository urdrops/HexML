import cv2
import serial
import time
from playsound import playsound
from simple_facerec import SimpleFacerec
import asyncio


async def send_serial(ser, name):
    data_to_send = f"AMIITY University Tashkent welcomes respected {name}\n"
    ser.write(data_to_send.encode())


async def async_play(path, name):
    if name != "":
        playsound(path)


async def main():
    srf = SimpleFacerec()
    srf.load_encoding_images("faces/")
    # Load Camera
    cap = cv2.VideoCapture(2)
    # serial to send result to arduino
    ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
    # time to connect
    time.sleep(2)
    prev_name = ''
    queue_faces = []

    # loop
    while True:
        ret, frame = cap.read()
        # detect faces
        face_locations, face_names = srf.detect_known_faces(frame)
        for face_loc, name in zip(face_locations, face_names):
            y1, x1, y2, x2 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            cv2.putText(frame, name, (x1, y1), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 100, 0), 4)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 100, 0), 4)
            # to check is None or not
            name_to_display = name if name != "" else prev_name
            if name_to_display != prev_name and name_to_display not in queue_faces:
                queue_faces.append(name_to_display)
                await send_serial(ser, name_to_display)
                await async_play(f"sounds/{name_to_display}.mp3", name_to_display)
                await send_serial(ser, name_to_display)
                prev_name = name_to_display
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
        if key == 48:
            print("Before:", queue_faces)
            queue_faces.clear()
            print("After:", queue_faces)
    ser.close()
    cap.release()
    cv2.destroyAllWindows()


asyncio.run(main())
