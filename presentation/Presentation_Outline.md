# Presentation Outline: Polarization Analysis of Erfurt–Sundhausen Fiber Link

**Estimated Duration**: 10 Minutes (~1 minute per slide)

## Slide 1: Title Slide
- **Title**: Polarization Analysis of the Erfurt–Sundhausen Fiber Link
- **Subtitle**: Investigating Temporal Behavior and Environmental Correlations
- **Presenter**: [Your Name]

## Slide 2: Introduction & Objective
- **What**: Analyzing continuous polarization measurements from an overhead optical fiber link.
- **Why**: To understand how environmental factors affect signal polarization.
- **Key Parameters**:
  1. **Azimuth**: Orientation of the polarization ellipse.
  2. **Ellipticity**: Shape of the polarization ellipse.
- **Primary Goal**: Evaluate the correlation between these parameters and environmental conditions, specifically **surface pressure**.

## Slide 3: Hardware & Data Acquisition
- **Measurement Hardware**: PAX1000IR2/M Polarimeter.
- **Data Resolution**: High-frequency sampling rate (~0.25 s / 3.9 Hz).
- **Scale**: Yields massive datasets requiring robust automated processing pipelines (e.g., 400MB+ per file).

## Slide 4: Automated Data Pipeline
- **Orchestration**: A fully automated 11-step Python pipeline (`run_pipeline.py`).
- **Data Pruning**: Initial sanitization, targeted error analysis, and filtering out outliers.
- **Frequency Analysis**: Utilization of Welch’s periodogram to detect periodic structural components in the signal.

## Slide 5: External Environmental Integration
- **Weather APIs**: Seamless integration with the Open-Meteo REST API.
- **Data Merging**: Crossing hardware polarimeter data with remote environmental metrics.
- **Specific Integrations**:
  - Surface Pressure
  - Daylight (Sunrise / Sunset timings)

## Slide 6: Interactive Analytical Dashboard
- **Web App**: Built cleanly using Streamlit (`dashboard.py`).
- **Functionality**:
  - Real-time exploratory data analysis (EDA).
  - Visualization of hourly pressure against azimuth/ellipticity trends.
  - Granular views simulating high-frequency polarization ellipse evolution.

## Slide 7: Methodology - Correlation & Trends
- **Daily Correlation**: Analyzing day-by-day metrics between weather and optical data.
- **Long-term Trends**: Smoothing noisy high-frequency signals into readable Hourly and Daily macroscopic trends.
- **Visualization Output**: Generation of comparative plots displaying statistical correlations.

## Slide 8: Technical Limitations & Challenges
- **Processing Power**: High-frequency signals mandate large memory footprints.
- **REST Rate Limits**: Constant fetching from weather APIs triggers rate-limiting (resolved via local caching strategies).
- **Data Volume**: Privacy and constraint logistics of handling gigabytes of raw sensor data logs.

## Slide 9: Conclusion & Next Steps
- **Summary**: Our pipeline successfully bridges low-level hardware measurement systems with high-level environmental APIs and interactive web dashboards.
- **Broader Impact**: A deeper understanding of environmental impacts on fiber optics improves infrastructure reliability.
- **Next Steps**: Introduce predictive modeling or machine learning for expected signal degradation.

## Slide 10: Q&A
- *Thank you for your time. Are there any questions?*
