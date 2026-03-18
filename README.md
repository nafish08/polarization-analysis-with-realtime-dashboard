# Polarization Analysis of Erfurt–Sundhausen Fiber Link

## Overview

This project analyzes polarization measurements from the Erfurt–Sundhausen overhead fiber link. The objective is to investigate the temporal behavior of polarization parameters (azimuth and ellipticity) and evaluate their correlation with environmental conditions, specifically **surface pressure**.

The toolset includes a complete data processing automation pipeline that sanitizes high-resolution hardware data, crosses it with remote environmental APIs, detects periodic components using Welch's periodogram, and ultimately spins up a sophisticated, highly-accessible interactive Streamlit dashboard.

---

## Features

- **Automated Data Pipeline (`run_pipeline.py`)**: A sequence of scripts that handle reading, cleaning, and filtering raw polarimeter data, as well as seamlessly merging it with automatically fetched weather and sunrise/sunset data (from Open-Meteo).
- **Interactive UI/UX Dashboard (`dashboard.py` / `run_dashboard.py`)**: A deeply organized, grid-based Streamlit web GUI completely powered by native **Plotly** engine integrations featuring:
  - Accessible, extremely high-contrast light-mode theming using the global Okabe-Ito colorblind-friendly palette.
  - Native Plotly navigation toolbars (Pan, Zoom, and embedded explicit `.jpg` Snapshot Downloads) bound explicitly to every single data viz.
  - Real-time exploratory data analysis of hourly pressure mapped explicitly side-by-side with azimuth and ellipticity trends.
  - Cleaned & precisely normalized Welch's 24-hour rhythmic periodograms (DC-component removed for distinct cyclic clarity).
  - High-frequency, time-windowed visualizations explicitly simulating and rendering physics models of polarization ellipse evolution.
  - Efficiently computed raw vs clean database anomaly breakdowns.

---

## Materials & Built With

This project relies on standard high-performance data science and numeric ecosystems:
- **Core Processing Engine**: Python, `pandas`, `numpy`, `scipy`
- **Data Visualization**: `plotly.express`, `plotly.graph_objects`, `matplotlib`, `streamlit`
- **External Integration**: `requests` for the Open-Meteo REST API.
- **Hardware Integration**: The project logic isolates parameters extracted from a **PAX1000IR2/M polarimeter** providing continuous reading sampled at ~0.25 s (an effective 3.9 Hz sampling rate).

---

## How to Install and Run

### 1. Prerequisites
- **Python 3.10+**
- The pipeline will automatically download the required raw measurement dataset from Zenodo into `data/raw/` on its first run.

### 2. Setup Environment
Clone the repository and spin up a local Python virtual environment to contain dependencies:

```bash
# Set up a virtual environment (venv)
python -m venv venv

# Activate environment
# Linux / Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install the required architecture packages
pip install -r requirements.txt
```

### 3. Run the Data Pipeline
Before you can view the dashboard, the backend data must be prepared. Instead of running all 11 scripts manually, you can instantly run the automated pipeline orchestrator:

```bash
python run_pipeline.py
```
This wrapper script will sequentially execute the analysis pipeline (from `01_inspect_raw_data.py` up to `11_bonus_visualizations.py`), fetching missing weather data, purging broken timeline indices, and structuring everything into optimized `data/processed/` nodes.

### 4. Run the Dashboard
Once the pipeline has populated the directories, execute the app launcher:

```bash
python run_dashboard.py
```
*Note: Using `run_dashboard.py` is safely recommended over `streamlit run dashboard.py` directly, as it intrinsically patches out Windows-specific `asyncio` event-loop runtime exceptions.*

Open the local URL provided in your console (e.g., `http://localhost:8501`) in a web browser to dive into your analytics.

---

## Project Structure

```text
polarization_project_erfurt_sundhausen/
│
├── data/
│   ├── raw/                # The colossal source polarimeter datasets (auto-downloaded)
│   ├── processed/          # Intermediary cleaned datasets and merged results
│   └── external/           # Weather & daylight contextual data
│
├── presentation/           # PowerPoint presentations and MD slide outlines
├── scripts/                # The step-by-step logic scripts (01 to 11)
├── outputs/                # Generated figures and analysis tables
│
├── run_pipeline.py         # Entry point for the data pipeline
├── dashboard.py            # Streamlit dashboard layout using Plotly grids
├── run_dashboard.py        # Entry point for the interactive dashboard
├── README.md               # This documentation
└── requirements.txt        # Python dependency manifest
```

---

## Limitations

- **Git Version Control Blockers**: By default, `.gitignore` rules prevent synchronization of `.csv` blobs and the `/data/` and `/outputs/` ecosystem trees to prevent violating GitHub limit thresholds.
- **Automated Downloads**: The heavy raw measurement data (`data/raw/`) is not bundled directly inside this repo but gracefully fetched upon running the engine.
- **Processing Constraints**: The pipeline strictly processes high-frequency signals. Depending on local hardware overhead, the terminal matrix joins and spectrogram rendering scripts might pull prominent memory chunks. 
- **API Rate Limits**: The Open-Meteo REST API is extensively queried for sunrise/sunset times. Batch or redundant parallel triggers on `05_fetch_sunrise_sunset.py` may trigger temporary upstream API blockades. Cached CSV architectures usually protect against this after the first pull."# polarization-analysis-with-realtime-dashboard" 
