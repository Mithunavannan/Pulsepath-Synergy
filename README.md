
# 🚦 AI-Based Smart Traffic Signal Management System

![Python](https://img.shields.io/badge/Python-3.10-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Object%20Detection-red)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![Edge AI](https://img.shields.io/badge/Edge-AI-orange)
![Status](https://img.shields.io/badge/Project-Prototype-success)

An **AI-powered adaptive traffic signal system** that dynamically adjusts traffic light timings using **real-time vehicle detection and density estimation**.

This system improves **traffic flow, reduces congestion, and prioritizes emergency vehicles** by replacing traditional **fixed-timer traffic signals** with an **intelligent computer vision-based controller**.

---

# 📌 Project Overview

Most traffic signals today operate on **fixed time intervals**, regardless of traffic conditions. This causes:

* Long waiting times
* Traffic congestion
* Fuel wastage
* Delays for emergency vehicles

This project introduces an **AI-based adaptive signal control system** that:

✅ Detects vehicles using **YOLOv8**
✅ Calculates **lane density dynamically**
✅ Uses **row-wise clustering for queue estimation**
✅ Assigns **dynamic green signal timing**
✅ Supports **emergency vehicle prioritization**
✅ Displays signals using **LED + LCD timers**

The system can be deployed in **smart cities, busy intersections, and intelligent transportation systems (ITS).**

---

# 🧠 Core Features

### 🚗 Real-Time Vehicle Detection

Vehicles are detected using **YOLOv8 deep learning model** trained on traffic datasets.

Detected vehicle classes:

* Motorcycle
* Car
* Auto
* Van
* Bus
* Truck

Detection pipeline:

```
Camera → YOLOv8 → Bounding Boxes → Vehicle Classification
```

---

### 📍 ROI-Based Lane Detection

To avoid unnecessary detections, the system analyzes vehicles **only inside a polygonal Region of Interest (ROI)** representing the traffic lane.

Benefits:

* Removes background noise
* Ignores vehicles from other roads
* Improves density accuracy

---

### 📦 Row-Wise Vehicle Clustering

Vehicles are grouped into **rows based on bottom Y-coordinates of bounding boxes**.

```
Signal
│
Row 1 → Closest vehicles
Row 2 → Next queue
Row 3 → Further queue
```

This approach estimates **queue length and congestion level**.

---

### 📊 Weighted Traffic Density Calculation

Each vehicle type contributes differently to lane congestion.

| Vehicle     | Weight |
| ----------- | ------ |
| Two-wheeler | 1      |
| Car         | 2      |
| Auto        | 2      |
| Van         | 3      |
| Bus         | 5      |
| Truck       | 5      |

Total density = **sum of vehicle weights**

---

### ⏱️ Adaptive Signal Timing

Signal timing is calculated from lane density.

| Density | Green Time |
| ------- | ---------- |
| <10     | 15s        |
| 11–20   | 20s        |
| 21–30   | 25s        |
| 31–40   | 30s        |
| ...     | ...        |
| Max     | 90s        |

This ensures:

✔ Shorter waiting time
✔ Faster traffic clearance
✔ Efficient intersection management

---

### 🚑 Emergency Vehicle Priority

Emergency vehicles such as:

* Ambulance
* Fire Truck
* Police Vehicles

can be detected and prioritized.

Future expansion:

* **LoRa-based early communication**
* Emergency detection **500 meters before intersection**
* Automatic signal override

---

# ⚙️ System Architecture

```
Traffic Camera
      │
      ▼
YOLOv8 Vehicle Detection
      │
      ▼
ROI Filtering
      │
      ▼
Row-wise Vehicle Clustering
      │
      ▼
Weighted Density Calculation
      │
      ▼
Dynamic Signal Timing Algorithm
      │
      ▼
Traffic Controller
      │
      ▼
LED Signals + Countdown Display
```

---

# 🖥️ Technology Stack

| Technology                | Purpose                  |
| ------------------------- | ------------------------ |
| Python                    | Core programming         |
| YOLOv8                    | Vehicle detection        |
| OpenCV                    | Video processing         |
| NumPy                     | Data computation         |
| ESP32-CAM                 | Camera module            |
| Raspberry Pi / BeagleBone | Edge processing          |
| TM1637                    | Countdown display        |
| LED Modules               | Traffic light simulation |

---

# 🔧 Hardware Prototype

The prototype intersection includes:

* **4 traffic lanes**
* **ESP32-CAM for vehicle detection**
* **Edge processor (Raspberry Pi / BeagleBone)**
* **LED traffic signals (Red / Yellow / Green)**
* **TM1637 display timers**
* **4×4 ft cardboard road model**

This setup simulates a **real traffic intersection**.

---

# 🔄 Traffic Signal Logic

System cycle:

```
Lane 1 → Lane 2 → Lane 3 → Lane 4 → repeat
```

Startup sequence:

```
All lanes → Yellow (15s)
```

For each lane:

```
Lane N → Green
Lane N+1 → Red with countdown
Other lanes → Red
```

After green:

```
Lane N → Yellow (5s)
Next lane activated
```

---

# 📊 Example Output

The system generates signal timing output in JSON format.

```json
{
 "Lane 1": {"green": 30, "red": 90},
 "Lane 2": {"green": 20, "red": 100},
 "Lane 3": {"green": 15, "red": 105},
 "Lane 4": {"green": 25, "red": 95}
}
```

This output is displayed on **LCD timers and LED signals**.

---

# 📈 Real-World Applications

* Smart City Infrastructure
* Intelligent Transportation Systems
* Urban Traffic Management
* Emergency Vehicle Priority Systems
* AI-based Traffic Monitoring

---

# 🚀 Future Enhancements

* Reinforcement Learning based signal optimization
* Cloud-based **traffic analytics dashboard**
* Multi-intersection coordination
* Vehicle violation detection
* Integration with **real traffic signal controllers**

---

# 👨‍💻 Author

**Mithunavannan JR**

AI Researcher | Computer Vision Developer
Project: **AI-Based Smart Traffic Signal Management System**

---

⭐ If you like this project, consider **starring the repository**.

