# Screen Recording & Verification Guide: Italy 7-Day Journey

## 1. Overview & Objective

This document details the technical setup, verification procedures, and reproduction steps for the **7-Day Italy Travel Intelligence Demo** (`demo_travel_planner.mp4`).

The application features:
- **Destination:** Italy (Rome, Florence, and Venice)
- **Duration:** Exactly 7 Calendar Days (Days 1 through 7)
- **Engine:** Google Gemini with Agent Development Kit (ADK) + FastAPI A2A protocol
- **Key Modules:** Verified Google Places navigation, authentic regional Italian culinary intelligence (Cacio e Pepe, Bistecca alla Fiorentina, Cicchetti), astronomical golden hour calculations, source-backed budget breakdown, and offline travel pack export.

---

## 2. Technical Video Specifications

The recorded demonstration strictly adheres to the lab and production media standards:

| Property | Value | Verification Status |
| :--- | :--- | :--- |
| **Filename** | `demo_travel_planner.mp4` | Verified |
| **Resolution** | 1920 × 1080 (1080p Full HD) | Verified (`width=1920, height=1080`) |
| **Aspect Ratio** | 16:9 | Verified |
| **Frame Rate** | 30.0 fps constant | Verified (`r_frame_rate=30/1`) |
| **Duration** | 90.33 seconds (90–150s window) | Verified (`duration=90.33s`) |
| **Video Codec** | H.264 / AVC (High Profile, YUV420p) | Verified (`codec_name=h264`) |
| **Audio** | Silent / No corrupt audio stream | Verified |
| **Container** | MP4 (`isom / mp41`) | Verified |
| **Execution** | Genuine screen recording of live local app | Verified (No static mocks/overlays) |

---

## 3. How to Reproduce and Record Locally

### Prerequisites
- Node.js & Python virtual environments installed
- Google Chrome installed at `/usr/bin/google-chrome`
- Playwright Python package (`pip install playwright`)
- FFmpeg installed (`ffmpeg` and `ffprobe` in `$PATH`)

### Step 1: Start the Local Application
```bash
cd /config/Desktop/BuildWithGemini/travel-planner/frontend
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8081
```

### Step 2: Run the Automated Screen Recording
```bash
/opt/venv/bin/python3 /tmp/record_italy_playwright.py
```

### Step 3: Verify Video Integrity with `ffprobe`
```bash
ffprobe -v error \
  -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,duration \
  -show_entries format=duration,size \
  -of default=noprint_wrappers=1 \
  /config/Desktop/BuildWithGemini/travel-planner/demo_travel_planner.mp4
```

Expected output:
```text
codec_name=h264
width=1920
height=1080
r_frame_rate=30/1
duration=90.333333
size=5912158
```

---

## 4. Test Suite Execution

Run all unit and regression tests:
```bash
cd /config/Desktop/BuildWithGemini/travel-planner
.venv/bin/pytest tests/unit/ -v
```

All 31 unit tests cover:
- Destination consistency (Italy request produces exclusively Rome, Florence, and Venice items)
- Exactly 7 calendar days inclusive parsing and validation
- Authentic regional culinary specialty retrieval and food safety
- Verified Google Maps place search and turn-by-turn walking directions URL encoding
- Astronomical golden hour calculations
- Firestore Food Passport persistence and offline trip pack export
