import cv2
from ultralytics import YOLO

model = YOLO(r"C:\Users\ADMIN\OneDrive\Pictures\cmli\best (6).pt")

cap = cv2.VideoCapture(r"C:\Users\ADMIN\OneDrive\Pictures\cmli\1.mp4")

cv2.namedWindow("YOLO Detection", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("YOLO Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    annotated_frame = results[0].plot()

    cv2.imshow("YOLO Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()