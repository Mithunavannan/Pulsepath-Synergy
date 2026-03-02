import cv2
import numpy as np
import time
import random
from ultralytics import YOLO

# ================= MODEL =================
model = YOLO(
    r"C:\Users\Diwakaran\Downloads\diwa traffic\Traffic-Intersection-Simulation-with-Stats"
    r"\AI-Based-Smart-Traffic-Management-System-with-Emergency-Vehicle-Prioritization"
    r"\best (6).pt"
)

# ================= BASE VIDEOS =================
base_videos = [
    r"C:\Users\Diwakaran\Downloads\diwa traffic\Traffic-Intersection-Simulation-with-Stats\1.mp4",
    r"C:\Users\Diwakaran\Downloads\diwa traffic\Traffic-Intersection-Simulation-with-Stats\2.mp4",
    r"C:\Users\Diwakaran\Downloads\diwa traffic\Traffic-Intersection-Simulation-with-Stats\3.mp4",
    r"C:\Users\Diwakaran\Downloads\diwa traffic\Traffic-Intersection-Simulation-with-Stats\4.mp4"
]

# ================= CREATE 16 FEEDS =================
INTERSECTIONS = 4
video_groups = [random.sample(base_videos, 4) for _ in range(INTERSECTIONS)]

# ================= ROI POLYGONS =================
roi_polygons = {
    i: {
        0: np.array([(269,66),(276,281),(496,267),(495,68),(271,66)],np.int32).reshape((-1,1,2)),
        1: np.array([(333,96),(333,262),(598,249),(562,96),(333,96)],np.int32).reshape((-1,1,2)),
        2: np.array([(262,123),(258,328),(490,322),(495,122),(473,125)],np.int32).reshape((-1,1,2)),
        3: np.array([(328,115),(325,312),(599,319),(561,114),(330,115)],np.int32).reshape((-1,1,2))
    } for i in range(4)
}

# ================= WEIGHTS =================
lane_weights = {
    "bike":1, "motorbike":1, "bicycle":1,
    "car":2, "van":2,
    "bus":3, "truck":3
}

def calculate_green_time(vehicle_counts):
    total = sum(lane_weights.get(k,1)*v for k,v in vehicle_counts.items())
    if total <= 10: return 15
    if total <= 20: return 20
    if total <= 30: return 25
    if total <= 40: return 30
    return min(90, 30 + ((total - 40)//10)*5)

# ================= INIT =================
intersections = []
for i in range(INTERSECTIONS):
    intersections.append({
        "caps": [cv2.VideoCapture(p) for p in video_groups[i]],
        "vehicle_counts": [{} for _ in range(4)],
        "vehicles_inside": [{} for _ in range(4)],
        "active_lane": 0,
        "phase": "GREEN",
        "remaining": 15,
        "last_update": time.time()
    })

cv2.namedWindow("City Traffic Control", cv2.WINDOW_NORMAL)

# ================= DASHBOARD (FIXED) =================
last_ui_update = 0
dashboard_cache = None

def draw_dashboard(height, data):
    panel = np.zeros((height, 420, 3), dtype=np.uint8)
    panel[:] = (18,18,18)

    y = 50

    # ---- TITLE ----
    cv2.putText(panel,"CENTRAL TRAFFIC DASHBOARD",(20,y),
                cv2.FONT_HERSHEY_SIMPLEX,0.95,(0,255,255),2,cv2.LINE_AA)
    y += 45
    cv2.line(panel,(20,y),(400,y),(80,80,80),2)
    y += 30

    for s, inter in enumerate(data):
        cv2.putText(panel,f"SIGNAL {s+1}",(20,y),
                    cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2,cv2.LINE_AA)
        y += 32

        for l in range(4):
            total = sum(inter["vehicle_counts"][l].values())
            state = "GREEN" if inter["active_lane"] == l else "RED"
            color = (0,220,0) if state=="GREEN" else (0,0,220)

            cv2.putText(panel,
                        f"Lane {l+1}: {state} | Vehicles: {total}",
                        (35,y),
                        cv2.FONT_HERSHEY_SIMPLEX,0.65,
                        color,2,cv2.LINE_AA)
            y += 26

        y += 15
        cv2.line(panel,(30,y),(390,y),(60,60,60),1)
        y += 30

    return panel

# ================= MAIN LOOP =================
while True:
    intersection_frames = []

    for idx, inter in enumerate(intersections):
        frames = []

        # ---- TIMER ----
        if time.time() - inter["last_update"] >= 1:
            inter["last_update"] = time.time()
            inter["remaining"] -= 1
            if inter["remaining"] <= 0:
                if inter["phase"] == "GREEN":
                    inter["phase"] = "YELLOW"
                    inter["remaining"] = 5
                else:
                    inter["active_lane"] = (inter["active_lane"] + 1) % 4
                    inter["phase"] = "GREEN"
                    inter["remaining"] = calculate_green_time(
                        inter["vehicle_counts"][inter["active_lane"]])

        # ---- LANES ----
        for lane_id, cap in enumerate(inter["caps"]):
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()

            frame = cv2.resize(frame,(640,360))
            poly = roi_polygons[idx][lane_id]

            current = {}
            inside = inter["vehicles_inside"][lane_id]
            counts = inter["vehicle_counts"][lane_id]

            results = model.track(frame, persist=True, device="cpu",
                                  conf=0.15, iou=0.25)

            if results and results[0].boxes is not None:
                boxes = results[0].boxes
                for i, box in enumerate(boxes.xyxy):
                    if boxes.id is None: continue
                    x1,y1,x2,y2 = map(int,box)
                    cx,cy = (x1+x2)//2,(y1+y2)//2
                    oid = int(boxes.id[i])
                    cls = model.names[int(boxes.cls[i])].lower()

                    if cv2.pointPolygonTest(poly,(cx,cy),False) >= 0:
                        current[oid] = cls
                        if oid not in inside:
                            inside[oid] = cls
                            counts[cls] = counts.get(cls,0)+1

                    cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,255),2)
                    cv2.putText(frame,cls,(x1,y1-5),
                                cv2.FONT_HERSHEY_SIMPLEX,0.5,
                                (0,255,255),1,cv2.LINE_AA)

            for oid in set(inside)-set(current):
                cls = inside[oid]
                counts[cls] = max(0,counts.get(cls,0)-1)
                del inside[oid]

            color = (0,255,0) if lane_id==inter["active_lane"] else (0,0,255)
            cv2.polylines(frame,[poly],True,color,2)

            frames.append(frame)

        # ---- INTERSECTION GRID ----
        grid = np.vstack((
            np.hstack((frames[0],frames[1])),
            np.hstack((frames[2],frames[3]))
        ))

        intersection_frames.append(grid)

    # ---- CITY GRID ----
    city_grid = np.vstack((
        np.hstack((intersection_frames[0],intersection_frames[1])),
        np.hstack((intersection_frames[2],intersection_frames[3]))
    ))

    # ---- DASHBOARD CACHE ----
    if dashboard_cache is None or time.time() - last_ui_update > 1:
        dashboard_cache = draw_dashboard(city_grid.shape[0], intersections)
        last_ui_update = time.time()

    cv2.imshow("City Traffic Control", np.hstack((city_grid, dashboard_cache)))

    time.sleep(0.02)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
