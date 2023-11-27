import cv2
from simple_facerec import SimpleFacerec
srf = SimpleFacerec()
srf.load_encoding_images("faces/")

# Load Camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    # detect faces
    face_locations, face_names = srf.detect_known_faces(frame)
    for face_loc, name in zip(face_locations, face_names):
        y1, x1, y2, x2 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

        cv2.putText(frame, name, (x1, y1), cv2.FONT_HERSHEY_DUPLEX, 1, (0,100,0), 4)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 100, 0), 4)
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:
        break
cap.release()
cv2.destroyAllWindows()