# Screen Recording & Verification Guide: Production-Grade Multi-Agent Italy 7-Day Journey

## 1. Overview & Objective

This document details the technical setup, verification procedures, and reproduction steps for the **Production-Grade Multi-Agent AI Travel Experience Demo** (`demo_travel_planner.mp4`).

The application features:
- **Destination:** Italy (Rome, Florence, and Venice)
- **Duration:** Exactly 7 Calendar Days (Days 1 through 7)
- **Architecture:** Purposeful Multi-Agent System (Agents A–H: Orchestrator, Discovery, Places & Food Verification, Itinerary Optimization, Transportation/Logistics, Budget/Trade-Off, Weather/Timing, QA/Consistency)
- **Real Trip Intelligence Engine:** Canonical trip state schema, evidence-backed recommendations, confidence states, feasibility report (verification density score, schedule conflict analysis, pacing rating).
- **Logistics & Transit:** Verified Frecciarossa high-speed rail corridors (Roma Termini ➔ Firenze SMN in 95 min, Firenze SMN ➔ Venezia Santa Lucia in 125 min) with direct station navigation links.
- **Dynamic Regional Food Explorer:** Grounded Italian culinary specialties across Lazio (Cacio e Pepe, Carbonara), Tuscany (Bistecca alla Fiorentina, Ribollita), and Veneto (Cicchetti, Baccalà Mantecato, Sarde in Saor) with Food Passport integration.
- **Offline Travel Pack:** Exportable, self-contained travel bundle with verified addresses and coordinates.

---

## 2. Technical Video Specifications

The recorded demonstration strictly adheres to production media standards:

| Property | Value | Verification Status |
| :--- | :--- | :--- |
| **Filename** | `demo_travel_planner.mp4` | Verified |
| **Resolution** | 1920 × 1080 (1080p Full HD) | Verified (`width=1920, height=1080`) |
| **Aspect Ratio** | 16:9 | Verified |
| **Frame Rate** | 30.0 fps constant | Verified (`r_frame_rate=30/1`) |
| **Duration** | 94.60 seconds (within 90–150s range) | Verified (`duration=94.60s`) |
| **File Size** | 6.17 MB (6,170,474 bytes) | Verified |
| **Video Codec** | H.264 / AVC (High Profile, YUV420p) | Verified (`codec_name=h264`) |
| **Audio** | Silent / No corrupt audio stream | Verified |
| **Container** | MP4 (`isom / mp41`) | Verified |
| **Execution** | Genuine screen recording of live local app | Verified (No static mocks/blank frames) |

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
/opt/venv/bin/python3 /tmp/record_multiagent_italy.py
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

Expected Output:
```
codec_name=h264
width=1920
height=1080
r_frame_rate=30/1
duration=94.600000
size=6170474
```

---

## 4. Video Flow Breakdown

1. **Initial Welcome (00:00 - 00:06):** Brand interface and multi-agent trip planner welcome bar.
2. **Prompt Submission (00:06 - 00:15):** User types 7-day Italy request covering Rome, Florence, and Venice with authentic food, attractions, and budget.
3. **Multi-Agent Trip Synthesis (00:15 - 00:20):** MultiAgentTravelOrchestrator coordinates Agents B–H, generating canonical trip state and Feasibility Report.
4. **Day 1–3 Rome Heritage (00:20 - 00:36):** Ancient Rome, Trastevere dining, Vatican, and Rione Monti with verified Google Maps & transit links.
5. **Day 4 Rome ➔ Florence Transfer (00:36 - 00:46):** Frecciarossa high-speed rail corridor (95m), Santa Maria del Fiore, and Trattoria Da Nerbone.
6. **Day 5 Florence Renaissance (00:46 - 00:54):** Uffizi, Ponte Vecchio, and Oltrarno artisan quarters.
7. **Day 6 Florence ➔ Venice Transfer (00:54 - 01:04):** Frecciarossa rail corridor (125m) to Venezia Santa Lucia, Grand Canal, and Rialto.
8. **Day 7 Venice Cannaregio (01:04 - 01:14):** Cannaregio Jewish Ghetto, cicchetti bàcari, and gondola lagoon finale.
9. **Authentic Regional Food Explorer (01:14 - 01:24):** Grounded specialties dynamically synced to Italy (Rome, Florence, and Venice).
10. **Food Passport & Seasonal Events (01:24 - 01:30):** Personal dish tracking and seasonal Italian festivals.
11. **Copilot Interaction & Offline Pack (01:30 - 01:34):** Context-aware Copilot quick action and offline travel pack generation.
