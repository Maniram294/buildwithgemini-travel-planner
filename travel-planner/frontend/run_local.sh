#!/bin/bash
export AGENT_ENGINE_RESOURCE_NAME="projects/513515792631/locations/us-east1/reasoningEngines/2175217729299021824"
export AGENT_DIRECTORY="app"
export PORT=8081
cd /config/Desktop/BuildWithGemini/travel-planner/frontend
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8081
