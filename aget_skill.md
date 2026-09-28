---
name: google-adk-travel-mas-builder
description: Generates, scaffolds, and implements a multi-agent travel booking and planning system using Google Agent Development Kit (ADK) in Python.
tools:
  - file_creator
  - python_executor
---

# Google ADK Multi-Agent Travel Planner Skill

## Goal
Generate a complete, production-ready Python Multi-Agent System (MAS) using `google-adk` that helps users discover low-cost flight itineraries, suggests "light booking" strategies (carry-on only, off-peak timing, avoiding hidden add-ons), and curates day-by-day sightseeing and neighborhood guides.

---

## Architectural Rules for Google ADK (Python)

When creating or modifying code for this project, always adhere to these rules:

1. **Framework Core Imports**:
   - Use `from google.adk import Agent, Workflow` (or `from google.adk.agents import LlmAgent`).
   - Use standard Google GenAI models such as `gemini-2.5-flash` or `gemini-flash-latest`.

2. **Agent Hierarchy**:
   - **Root Coordinator (`root_agent` / `MasterTravelPlanner`)**: Orchestrates the conversation, parses user constraints (origin, destination, dates, budget), routes tasks to sub-agents, and synthesizes the final travel package.
   - **Flight & Light Booking Specialist (`flight_agent`)**: Computes cheap routes, compares airlines, and details light booking advice (carry-on limits, seat selection fee avoidance, budget airline tips).
   - **Sightseeing & Local Guide Specialist (`sightseeing_agent`)**: Curates free and low-cost attractions, neighborhood routes, transit advice, and food recommendations.

3. **Tool & Skill Design**:
   - Provide concrete Python function tools with comprehensive docstrings and type annotations so the ADK runner can automatically parse schemas.
   - Separate domain logic into a `tools/` directory (e.g., `mock_flight_api`, `mock_attractions_api`).

---

## Target Project Structure to Generate

```text
travel_planner_adk/
├── .env.example
├── requirements.txt
├── tools/
│   ├── __init__.py
│   ├── flight_tools.py
│   └── sightseeing_tools.py
├── agent.py
