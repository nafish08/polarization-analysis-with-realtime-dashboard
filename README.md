# Polarization Analysis of Erfurt–Sundhausen Fiber Link

## Overview

This project analyzes polarization measurements from the Erfurt–Sundhausen overhead fiber link. The goal is to investigate how polarization parameters (azimuth and ellipticity) vary over time and whether they correlate with environmental factors, specifically **surface pressure**.

The analysis follows three main steps:

- **Part A:** Data preparation and error analysis  
- **Part B:** Correlation analysis with weather data  
- **Part C:** Visualization and interpretation  

---

## Dataset

### Polarization Data
- Source: Measurement file from PAX1000IR2/M polarimeter
- Sampling: ~0.25 s interval (~3.9 Hz effective)
- Parameters:
  - Azimuth [deg]
  - Ellipticity [deg]
  - Stokes parameters
  - Power metrics

### Weather Data
- Source: Open-Meteo API
- Variable used: **Surface pressure [hPa]**
- Resolution: 1 hour

### Sunrise / Sunset Data
- Source: Open-Meteo API
- Used for day/night contextual analysis

---

## Project Structure
polarization_project_erfurt_sundhausen/
│
├── data/
│ ├── raw/ # Raw measurement data (not included in repo)
│ ├── processed/ # Cleaned and merged datasets (not included)
│ └── external/ # Weather and sunrise/sunset data
│
├── scripts/ # Python analysis scripts
│ ├── 01_inspect_raw_data.py
│ ├── 02_clean_polarization_data.py
│ ├── 03_error_analysis.py
│ ├── 03b_filter_data.py
│ ├── 04_fetch_weather_data.py
│ ├── 05_fetch_sunrise_sunset.py
│ ├── 06_merge_datasets.py
│ ├── 07_daily_correlation_analysis.py
│ ├── 08_trend_analysis.py
│ ├── 09_plot_three_days.py
│ ├── 10_plot_polarization_ellipses.py
│ └── 11_bonus_visualizations.py
│
├── outputs/
│ ├── figures/ # Generated plots
│ ├── tables/ # Analysis results
│ └── logs/ # Reports (ignored in Git)
│
├── README.md
└── requirements.txt


---

## Installation

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

pip install -r requirements.txt

Run all scripts in sequence:
python scripts/01_inspect_raw_data.py
python scripts/02_clean_polarization_data.py
python scripts/03_error_analysis.py
python scripts/03b_filter_data.py
python scripts/04_fetch_weather_data.py
python scripts/05_fetch_sunrise_sunset.py
python scripts/06_merge_datasets.py
python scripts/07_daily_correlation_analysis.py
python scripts/08_trend_analysis.py
python scripts/09_plot_three_days.py
python scripts/10_plot_polarization_ellipses.py
python scripts/11_bonus_visualizations.py