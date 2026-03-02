import cv2
import numpy as np
import json
import time
from ultralytics import YOLO


model = YOLO(r"C:\Users\Diwakaran\Downloads\diwa traffic\Traffic-Intersection-Simulation-with-Stats\AI-Based-Smart-Traffic-Management-System-with-Emergency-Vehicle-Prioritization\best (6).pt")

video_paths = [
    r"C:\Users\Diwakaran\Downloads\diwa traffic\Traffic-Intersection-Simulation-with-Stats\1.mp4",
    r"C:\Users\Diwakaran\Downloads\diwa traffic\Traffic-Intersection-Simulation-with-Stats\2.mp4",
    r"C:\Users\Diwakaran\Downloads\diwa traffic\Traffic-Intersection-Simulation-with-Stats\3.mp4",
    r"C:\Users\Diwakaran\Downloads\diwa traffic\Traffic-Intersection-Simulation-with-Stats\4.mp4"
]

caps = [cv2.VideoCapture(path) for path in video_paths]
for idx, cap in enumerate(caps):
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_paths[idx]}")
        exit()

polygon_points_list = [
    np.array([(467, 190), (467, 195), (464, 330), (766, 330), (578, 190)], np.int32).reshape((-1, 1, 2)),
    np.array([(460, 195), (466, 197), (456, 330), (766, 330), (581, 201)], np.int32).reshape((-1, 1, 2)),
    np.array([(462, 200), (463, 198), (463, 335), (798, 335), (574, 193)], np.int32).reshape((-1, 1, 2)),
    np.array([(470, 202), (470, 202), (467, 320), (789, 320), (584, 203)], np.int32).reshape((-1, 1, 2))
]


lane_weights = {
    "bike": 1, "motorbike": 1, "bicycle": 1,
    "car": 2, "van": 2,
    "bus": 3, "truck": 3
}

vehicle_counts_list = [{} for _ in range(4)]
vehicles_inside_list = [{} for _ in range(4)]

active_lane_idx = 0
phase = "GREEN"
remaining_time = 15
yellow_time = 5
last_update = time.time()

final_lane_timings = [{} for _ in range(4)]

cv2.namedWindow("Traffic Surveillance", cv2.WINDOW_NORMAL)

def calculate_green_time(vehicle_counts):
    """Calculate green time based on weighted vehicle density"""
    total_lane_weight = 0
    for vtype, count in vehicle_counts.items():
        weight = lane_weights.get(vtype, 1)
        total_lane_weight += count * weight

    if total_lane_weight <= 10:
        green_time = 15
    elif 11 <= total_lane_weight <= 20:
        green_time = 20
    elif 21 <= total_lane_weight <= 30:
        green_time = 25
    elif 31 <= total_lane_weight <= 40:
        green_time = 30
    else:
        green_time = min(90, 30 + ((total_lane_weight - 40) // 10) * 5)

    return max(15, min(90, green_time))

def draw_signal_info(frame, lane_states, x=20, y=30):
    """Overlay lane signal states"""
    y_offset = y
    for lane, info in lane_states.items():
        text = f"{lane}: {info['state']} - {info['time']}s"
        color = (0, 255, 0) if info['state']=="GREEN" else (0, 255, 255) if info['state']=="YELLOW" else (0, 0, 255)
        cv2.putText(frame, text, (x, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, color, 2, cv2.LINE_AA)
        y_offset += 30
    return frame

while True:
    frames = []
    for idx, cap in enumerate(caps):
        ret, frame = cap.read()
        if not ret:
            frame = np.zeros((540, 960, 3), dtype=np.uint8)
        else:
            frame = cv2.resize(frame, (960, 540))
        frames.append(frame)

    if all([np.count_nonzero(frame) == 0 for frame in frames]):
        print("End of all video streams.")
        break

    processed_frames = []
    lane_states = {}

    if time.time() - last_update >= 1:  # every second
        last_update = time.time()
        remaining_time -= 1
        if remaining_time <= 0:
            if phase == "GREEN":
                phase = "YELLOW"
                remaining_time = yellow_time
            elif phase == "YELLOW":
                # Save final timings for this lane
                green_time = calculate_green_time(vehicle_counts_list[active_lane_idx])
                final_lane_timings[active_lane_idx] = {
                    "Green_Time_Seconds": green_time,
                    "Yellow_Time_Seconds": yellow_time,
                    "Red_Time_Seconds": 0
                }
                # Switch to next lane
                active_lane_idx = (active_lane_idx + 1) % 4
                phase = "GREEN"
                remaining_time = calculate_green_time(vehicle_counts_list[active_lane_idx])

    # Process frames with YOLO
    for idx, frame in enumerate(frames):
        if np.count_nonzero(frame) == 0:
            processed_frames.append(frame)
            continue

        polygon_points = polygon_points_list[idx]
        vehicle_counts = vehicle_counts_list[idx]
        vehicles_inside = vehicles_inside_list[idx]

        results = model.track(frame, persist=True, device='cpu', iou=0.25, conf=0.1)
        current_vehicles = {}

        if results and hasattr(results[0], "boxes"):
            boxes = results[0].boxes
            for i, box in enumerate(boxes.xyxy):
                x1, y1, x2, y2 = map(int, box[:4])
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                if boxes.id is not None:
                    object_id = int(boxes.id[i].item())
                else:
                    continue
                detected_class = int(boxes.cls[i].item())
                class_name = model.names.get(detected_class, "Unknown").lower()

                inside = cv2.pointPolygonTest(polygon_points, (center_x, center_y), False) >= 0
                if inside:
                    current_vehicles[object_id] = class_name
                    if object_id not in vehicles_inside:
                        vehicles_inside[object_id] = class_name
                        vehicle_counts[class_name] = vehicle_counts.get(class_name, 0) + 1

                color_map = {"car": (0, 255, 255), "bike": (0, 255, 255), "motorbike": (0, 255, 255),
                             "bus": (255, 0, 0), "van": (255, 0, 0), "truck": (255, 0, 0)}
                color = color_map.get(class_name, (0, 255, 0))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{class_name}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Remove exited vehicles
        exited = set(vehicles_inside.keys()) - set(current_vehicles.keys())
        for object_id in exited:
            class_name = vehicles_inside[object_id]
            if vehicle_counts.get(class_name, 0) > 0:
                vehicle_counts[class_name] -= 1
            del vehicles_inside[object_id]

        cv2.polylines(frame, [polygon_points], isClosed=True, color=(0, 0, 255), thickness=2)

        # --- Lane state display ---
        if idx == active_lane_idx:
            lane_states[f"Lane_{idx+1}"] = {"state": phase, "time": remaining_time}
            cv2.putText(frame, "ACTIVE", (800, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        else:
            lane_states[f"Lane_{idx+1}"] = {"state": "RED", "time": 0}

        processed_frames.append(frame)

    # Combine 4 feeds
    top = np.hstack((processed_frames[0], processed_frames[1]))
    bottom = np.hstack((processed_frames[2], processed_frames[3]))
    grid_frame = np.vstack((top, bottom))

    # Overlay timing dashboard
    grid_frame = draw_signal_info(grid_frame, lane_states, 20, 40)

    cv2.imshow("Traffic Surveillance", grid_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Final report
print("\n\n--- Final Lane Timings Report ---\n")
for idx in range(4):
    timing = final_lane_timings[idx]
    if timing:
        print(f"Lane {idx+1}: {timing}")

for cap in caps:
    cap.release()
cv2.destroyAllWindows()
