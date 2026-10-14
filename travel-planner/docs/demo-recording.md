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
- **Trip Copilot Targeted Replanning:** Context-aware replanning replacing Day 1 lunch with a casual trattoria while preserving surrounding activities and recalculating budget deterministically.
- **Persistent Saved Trips:** Browser `localStorage` save and restore lifecycle with modal management.
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
| **Duration** | 61.76 seconds | Verified (`duration=61.766667`) |
| **File Size** | 2.45 MB (2,458,363 bytes) | Verified |
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
PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright \
  /config/Desktop/BuildWithGemini/travel-planner/.venv/bin/python /tmp/record_phase7_full_demo.py
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
duration=61.766667
duration=61.766667
size=2458363
```

---

## 4. Video Flow Breakdown

1. **Initial Welcome (00:00 - 00:04):** Brand interface and multi-agent trip planner welcome bar.
2. **Prompt Submission (00:04 - 00:10):** User enters 7-day Italy request covering Rome, Florence, and Venice.
3. **Multi-Agent Trip Synthesis (00:10 - 00:14):** MultiAgentTravelOrchestrator generates canonical trip state and Feasibility Report (`87/100`).
4. **Day 1–3 Rome Heritage (00:14 - 00:22):** Ancient Rome, Colosseum, Roman Forum, Trastevere dining with verified Google Maps links.
5. **Day 4 Rome ➔ Florence Transfer (00:22 - 00:26):** Frecciarossa high-speed rail corridor (95m), Santa Maria del Fiore, and Trattoria Da Nerbone.
6. **Day 6 Florence ➔ Venice Transfer (00:26 - 00:30):** Frecciarossa rail corridor (125m) to Venezia Santa Lucia, Grand Canal, and Rialto.
7. **Authentic Regional Food Explorer (00:30 - 00:37):** Grounded specialties dynamically filtered by Florence and Venice.
8. **Budget Breakdown View (00:37 - 00:41):** Deterministic category cost breakdown and verification integrity badge.
9. **Trip Copilot Targeted Replanning (00:41 - 00:49):** Replaces Day 1 lunch with casual trattoria, recalculates budget, and preserves surrounding activities.
10. **Saved Trips Persistence (00:49 - 00:61):** Saves trip to local storage, opens Saved Trips modal, and displays persistent trip management.
