import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
from scipy.signal import welch
import asyncio
import sys
import io

# Windows asyncio bug workaround for Streamlit
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

st.set_page_config(page_title="Polarization Dashboard", layout="wide")

@st.cache_data
def load_data(file_path):
    if not file_path.exists():
        return None
    return pd.read_csv(file_path, parse_dates=["timestamp"])

def get_project_root():
    return Path(__file__).resolve().parent

DATA_DIR = get_project_root() / "data" / "processed"

# Streamlit natively handles background inheritance

# Accessible, high-contrast palette (Okabe-Ito)
COLOR_AZ = "#0072B2" # Blue
COLOR_EL = "#D55E00" # Vermillion
COLOR_PR = "#009E73" # Bluish Green
COLOR_ELLIPSE = "#CC79A7" # Reddish Purple

DL_CONFIG = {
  'toImageButtonOptions': {
    'format': 'jpeg',
    'filename': 'chart_download',
    'height': 600,
    'width': 1000,
    'scale': 2
  },
  'displaylogo': False
}

st.title("📡 Polarization Analysis Dashboard")
st.markdown("Real-time monitoring of the Erfurt-Sundhausen Fiber Link.")

tab1, tab2, tab3, tab4 = st.tabs(["Overview & Trends", "Daily Details", "Ellipse Evolution", "Data Quality"])

with tab1:
    hourly_file = DATA_DIR / "polarization_weather_merged_hourly.csv"
    hourly_df = load_data(hourly_file)
    
    if hourly_df is None:
        st.warning(f"Could not find merged hourly data at `{hourly_file}`. Have you run the pipeline yet?")
    else:
        # Metrics Grid Card
        with st.container(border=True):
            st.subheader("📊 Key Metrics")
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Days Checked", f"{len(hourly_df)/24:.1f}")
            if "azimuth_deg" in hourly_df.columns:
                m2.metric("Mean Azimuth", f"{hourly_df['azimuth_deg'].mean():.2f}°")
            if "ellipticity_deg" in hourly_df.columns:
                m3.metric("Mean Ellipticity", f"{hourly_df['ellipticity_deg'].mean():.2f}°")

        st.markdown("### 📈 Interactive Time Series")
        
        # Combined Plot Card (Full Width)
        with st.container(border=True):
            df_melted = hourly_df.melt(id_vars=['timestamp'], value_vars=['azimuth_deg', 'ellipticity_deg'], var_name='Parameter', value_name='Degrees')
            fig_comb = px.line(df_melted, x='timestamp', y='Degrees', color='Parameter', title="", color_discrete_map={"azimuth_deg": COLOR_AZ, "ellipticity_deg": COLOR_EL})
            fig_comb.update_yaxes(matches=None, showticklabels=True)
            fig_comb.update_layout(height=400)
            
            st.markdown("**Azimuth & Ellipticity Combined**", help="""**What does this show?**
Overlaying both Azimuth (rotation angle) and Ellipticity (shape) over time.

**Why does it matter?**
Seeing them on the same timeline reveals if severe rotation perfectly correlates with geometric shape distortion. If both lines jump or shift simultaneously, a massive external physical force (like air pressure or wind) simultaneously crushed and twisted the fiber optic cable.""")
            st.plotly_chart(fig_comb, use_container_width=True, config=DL_CONFIG)

        # Split Card Grid (2 Columns)
        col_ts1, col_ts2 = st.columns(2)
        with col_ts1:
            with st.container(border=True):
                fig_az = px.line(hourly_df, x='timestamp', y='azimuth_deg', title="Azimuth [°]", color_discrete_sequence=[COLOR_AZ])
                fig_az.update_yaxes(matches=None, showticklabels=True)
                fig_az.update_layout(height=350)
                st.plotly_chart(fig_az, use_container_width=True, config=DL_CONFIG)
                
        with col_ts2:
            with st.container(border=True):
                fig_el = px.line(hourly_df, x='timestamp', y='ellipticity_deg', title="Ellipticity [°]", color_discrete_sequence=[COLOR_EL])
                fig_el.update_yaxes(matches=None, showticklabels=True)
                fig_el.update_layout(height=350)
                st.plotly_chart(fig_el, use_container_width=True, config=DL_CONFIG)

        col_pr, col_psd = st.columns(2)
        
        with col_pr:
            with st.container(border=True):
                fig_pr = px.line(hourly_df, x='timestamp', y='surface_pressure_hpa', title="Surface Pressure [hPa]", color_discrete_sequence=[COLOR_PR])
                fig_pr.update_yaxes(matches=None, showticklabels=True)
                fig_pr.update_layout(height=350)
                st.plotly_chart(fig_pr, use_container_width=True, config=DL_CONFIG)
                
        with col_psd:
            with st.container(border=True):
                # Limit to the LATEST 3 DAYS only for the Daily Heartbeat (as requested)
                # This keeps the 'average' focused and easy to explain
                all_dates = sorted(hourly_df['timestamp'].dt.date.unique())
                latest_3_days = all_dates[-3:]
                analysis_df = hourly_df[hourly_df['timestamp'].dt.date.isin(latest_3_days)].copy()
                
                analysis_df['hour_only'] = analysis_df['timestamp'].dt.hour
                diurnal_profile = analysis_df.groupby('hour_only')[['azimuth_deg', 'ellipticity_deg', 'surface_pressure_hpa']].mean().reset_index()
                
                # Identify the specific 3 days used
                unique_days = sorted(analysis_df['timestamp'].dt.strftime('%b %d, %Y').unique())
                days_str = " & ".join(unique_days)
                
                # Normalize for easier comparison (0 to 1 scale)
                for col in ['azimuth_deg', 'ellipticity_deg', 'surface_pressure_hpa']:
                    c_min, c_max = diurnal_profile[col].min(), diurnal_profile[col].max()
                    if c_max > c_min:
                        diurnal_profile[f'{col}_norm'] = (diurnal_profile[col] - c_min) / (c_max - c_min)
                    else:
                        diurnal_profile[f'{col}_norm'] = 0.5
                
                fig_diurnal = go.Figure()
                fig_diurnal.add_trace(go.Scatter(x=diurnal_profile['hour_only'], y=diurnal_profile['azimuth_deg_norm'], mode='lines+markers', name='Azimuth (Avg)', line=dict(color=COLOR_AZ)))
                fig_diurnal.add_trace(go.Scatter(x=diurnal_profile['hour_only'], y=diurnal_profile['ellipticity_deg_norm'], mode='lines+markers', name='Ellipticity (Avg)', line=dict(color=COLOR_EL)))
                fig_diurnal.add_trace(go.Scatter(x=diurnal_profile['hour_only'], y=diurnal_profile['surface_pressure_hpa_norm'], mode='lines', name='Pressure (Avg)', line=dict(color=COLOR_PR, dash='dash')))
                
                fig_diurnal.update_layout(
                    title=f"",
                    xaxis_title="Hour of Day (0-23h)",
                    yaxis_title="Normalized Trend (Min to Max)",
                    height=350,
                    margin=dict(t=50, b=0, l=0, r=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.markdown(f"**24-Hour Daily Rhythms ({days_str})**", help=f"**What does this show?**\nThis simplifies your data from {days_str} into a single 'Average Day' cycle.\n\n**Why does it matter?**\nIt proves the 'Daily Rhythm' visually by showing the laser predictably rotates as the sun heats up the earth.")
                st.plotly_chart(fig_diurnal, use_container_width=True, config=DL_CONFIG)

with tab2:
    if hourly_df is not None:
        hourly_df["date_str"] = hourly_df["timestamp"].dt.strftime("%Y-%m-%d")
        available_days = ["All Dates"] + sorted(hourly_df["date_str"].unique())
        
        # User Setting Grid
        with st.container(border=True):
            st.subheader("📅 Filter Data")
            col_sel, _ = st.columns([1, 2])
            with col_sel:
                selected_day = st.selectbox("Select a computing window", available_days)
        
        if available_days:
            if selected_day == "All Dates":
                day_df = hourly_df
            else:
                day_df = hourly_df[hourly_df["date_str"] == selected_day]
            
            day_df = day_df.copy()
            day_df['hour'] = day_df['timestamp'].dt.hour
            
            st.markdown(f"### 🌦️ Weather Correlation ({selected_day})")
            
            # Scatter Plot Grid
            col_sc1, col_sc2 = st.columns(2)
            with col_sc1:
                with st.container(border=True):
                    fig_s_az = px.scatter(day_df, x="surface_pressure_hpa", y="azimuth_deg", color="hour", title="", color_continuous_scale='Viridis')
                    fig_s_az.update_layout(height=450)
                    # Manual trendline via numpy (no statsmodels needed)
                    _valid_az = day_df[["surface_pressure_hpa", "azimuth_deg"]].dropna()
                    if len(_valid_az) > 1:
                        _m, _b = np.polyfit(_valid_az["surface_pressure_hpa"], _valid_az["azimuth_deg"], 1)
                        _x_range = np.linspace(_valid_az["surface_pressure_hpa"].min(), _valid_az["surface_pressure_hpa"].max(), 100)
                        fig_s_az.add_trace(go.Scatter(x=_x_range, y=_m * _x_range + _b, mode="lines", name="Trend", line=dict(color="red", width=2, dash="solid")))
                    st.markdown("**Azimuth vs Pressure**", help="""**What does this show?**
Maps the laser's physical rotation against the weather's atmospheric surface pressure.

**Why does it matter?**
The red trendline directly calculates the causation. If the line angles up or down, it is mathematical proof that rising outdoor pressure specifically twists the glass fiber.""")
                    st.plotly_chart(fig_s_az, use_container_width=True, config=DL_CONFIG)
                    
            with col_sc2:
                with st.container(border=True):
                    fig_s_el = px.scatter(day_df, x="surface_pressure_hpa", y="ellipticity_deg", color="hour", title="", color_continuous_scale='Viridis')
                    fig_s_el.update_layout(height=450)
                    # Manual trendline via numpy (no statsmodels needed)
                    _valid_el = day_df[["surface_pressure_hpa", "ellipticity_deg"]].dropna()
                    if len(_valid_el) > 1:
                        _m, _b = np.polyfit(_valid_el["surface_pressure_hpa"], _valid_el["ellipticity_deg"], 1)
                        _x_range = np.linspace(_valid_el["surface_pressure_hpa"].min(), _valid_el["surface_pressure_hpa"].max(), 100)
                        fig_s_el.add_trace(go.Scatter(x=_x_range, y=_m * _x_range + _b, mode="lines", name="Trend", line=dict(color="red", width=2, dash="solid")))
                    st.markdown("**Ellipticity vs Pressure**", help="""**What does this show?**
Maps how 'squashed' the laser beam gets compared to the weather's atmospheric surface pressure.

**Why does it matter?**
A steep red trendline proves that the sheer heavy weight of the atmosphere is physically crushing the microscopic geometry of the glass cable.""")
                    st.plotly_chart(fig_s_el, use_container_width=True, config=DL_CONFIG)
        else:
            st.info("No daily data available.")

with tab3:
    hf_file = DATA_DIR / "polarization_weather_merged_highfreq.csv"
    hf_df = load_data(hf_file)
    if hf_df is None:
        st.warning(f"Could not find high-frequency data at `{hf_file}`.")
    else:
        hf_df["date_str"] = hf_df["timestamp"].dt.strftime("%Y-%m-%d")
        available_hf_days = sorted(hf_df["date_str"].unique())
        
        # Filter Grid
        with st.container(border=True):
            st.subheader("📅 Visualizer Settings")
            col_hfs, _ = st.columns([1, 2])
            with col_hfs:
                sel_day = st.selectbox("Select day for visualization", available_hf_days, key="hf_day")
                
        hf_day_df = hf_df[hf_df["date_str"] == sel_day].copy()
        
        # Dual Grid Layout (Controls left, Plots Right)
        col_ctrl, col_plots = st.columns([1, 3])
        with col_ctrl:
            with st.container(border=True):
                st.subheader("🕹️ Tuning Options")
                sl_start = st.slider("Time step (Start Index)", 0, max(0, len(hf_day_df)-10), 0)
                window_size = st.slider("Window length (Samples)", 10, 500, 100)
                subset = hf_day_df.iloc[sl_start : sl_start + window_size].copy()
                
                if not subset.empty:
                    last_pt = subset.iloc[-1]
                    st.success(f"**Viewing Ellipse At:**\n{last_pt['timestamp']}")
        
        with col_plots:
            if not subset.empty:
                subset["time_index"] = np.arange(len(subset))
                
                col_viz1, col_viz2 = st.columns(2)
                with col_viz1:
                    with st.container(border=True):
                        st.markdown("**Drift in Parameter Space** ", help="""**What does this show?**
Maps the entire Azimuth vs Ellipticity collision boundary over the entire selected block. Color indicates the progression of time forward.

**Why does it matter?**
A tight circle block means the laser is stable. If the dots streak wildly or shift entirely across the geometric map, the fiber is actively twisting apart in real-time.""")
                        fig_drift, ax_drift = plt.subplots(figsize=(5,5))
                        scatter = ax_drift.scatter(subset["azimuth_deg"], subset["ellipticity_deg"], c=subset["time_index"], s=15, cmap="viridis")
                        plt.colorbar(scatter, label="Time Progression ->")
                        ax_drift.set_xlabel("Azimuth [deg]")
                        ax_drift.set_ylabel("Ellipticity [deg]")
                        st.pyplot(fig_drift)
                        buf_drift = io.BytesIO()
                        fig_drift.savefig(buf_drift, format="jpg", bbox_inches='tight', dpi=300)
                        st.download_button(label="📸 Download Chart", data=buf_drift.getvalue(), file_name="drift_parameter_space.jpg", mime="image/jpeg", key="dl_drift", use_container_width=True)
                    
                with col_viz2:
                    with st.container(border=True):
                        st.markdown("**Live Ellipse Preview** ", help="""**What does this show?**
A literal 2D geometric cross-section of the laser beam at the exact split-second `t` you locked on the slider.

**Why does it matter?**
You are physically seeing the real-time optical shape of the beam being warped by external environmental pressure outside the glass.""")
                        psi = np.deg2rad(last_pt["azimuth_deg"])
                        chi = np.deg2rad(last_pt["ellipticity_deg"])
                        a = 1.0
                        b = np.clip(np.tan(chi), -1.0, 1.0)
                        t = np.linspace(0, 2*np.pi, 200)
                        x0 = a * np.cos(t)
                        y0 = b * np.sin(t)
                        x = x0 * np.cos(psi) - y0 * np.sin(psi)
                        y = x0 * np.sin(psi) + y0 * np.cos(psi)
                        
                        fig_ell, ax_ell = plt.subplots(figsize=(5,5))
                        ax_ell.plot(x, y, color=COLOR_ELLIPSE, linewidth=2)
                        ax_ell.axhline(0, color="gray", linewidth=0.5, linestyle="--")
                        ax_ell.axvline(0, color="gray", linewidth=0.5, linestyle="--")
                        ax_ell.set_aspect("equal", "box")
                        ax_ell.set_xlim(-1.2, 1.2)
                        ax_ell.set_ylim(-1.2, 1.2)
                        st.pyplot(fig_ell)
                        buf_ell = io.BytesIO()
                        fig_ell.savefig(buf_ell, format="jpg", bbox_inches='tight', dpi=300)
                        st.download_button(label="📸 Download Ellipse", data=buf_ell.getvalue(), file_name="live_ellipse_preview.jpg", mime="image/jpeg", key="dl_ell", use_container_width=True)

                with st.container(border=True):
                    st.markdown("**Polarization Ellipse Evolution (t, t+1s, t+1m, t+1h)** ", help="""**What does this show?**
Overlays 4 completely separate cross-sections of the identical laser beam taken at 4 different moments in time (`t`, `1 sec later`, `1 min later`, `1 hr later`).

**Why does it matter?**
By stacking them, we can physically measure the *velocity* of the distortion. Rapid shifts indicate fast wind/pressure drops, while slow hourly shifts map perfectly to the thermal gradient of the sun.""")
                    
                    base_time = last_pt["timestamp"]
                    target_times = [
                        (f"t", base_time),
                        ("t+1s", base_time + pd.Timedelta(seconds=1)),
                        ("t+1min", base_time + pd.Timedelta(minutes=1)),
                        ("t+1h", base_time + pd.Timedelta(hours=1))
                    ]
                    
                    fig_evo, ax_evo = plt.subplots(figsize=(8,8))
                    evo_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
                    
                    hf_indexed = hf_day_df.copy().set_index("timestamp").sort_index()
                    
                    for i, (lbl, tgt_t) in enumerate(target_times):
                        try:
                            idx = hf_indexed.index.get_indexer([tgt_t], method='nearest')[0]
                            row = hf_indexed.iloc[idx]
                            actual_time = hf_indexed.index[idx]
                            
                            psi = np.deg2rad(row["azimuth_deg"])
                            chi = np.deg2rad(row["ellipticity_deg"])
                            a = 1.0
                            b = np.clip(np.tan(chi), -1.0, 1.0)
                            t_arr = np.linspace(0, 2*np.pi, 200)
                            x0 = a * np.cos(t_arr)
                            y0 = b * np.sin(t_arr)
                            x = x0 * np.cos(psi) - y0 * np.sin(psi)
                            y = x0 * np.sin(psi) + y0 * np.cos(psi)
                            
                            time_str = actual_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]
                            
                            ax_evo.plot(x, y, color=evo_colors[i], linewidth=2, label=f"{lbl}: {time_str}")
                        except Exception:
                            pass
                            
                    ax_evo.axhline(0, color="gray", linewidth=0.5, linestyle="--")
                    ax_evo.axvline(0, color="gray", linewidth=0.5, linestyle="--")
                    ax_evo.set_aspect("equal", "box")
                    ax_evo.set_xlim(-1.2, 1.2)
                    ax_evo.set_ylim(-1.2, 1.2)
                    ax_evo.set_xlabel("Ex")
                    ax_evo.set_ylabel("Ey")
                    ax_evo.legend(loc="upper left")
                    
                    st.pyplot(fig_evo)
                    buf_evo = io.BytesIO()
                    fig_evo.savefig(buf_evo, format="jpg", bbox_inches='tight', dpi=300, facecolor="white")
                    st.download_button(label="📸 Download Evolution Graph", data=buf_evo.getvalue(), file_name="ellipse_evolution.jpg", mime="image/jpeg", key="dl_evo", use_container_width=True)

with tab4:
    wrong_file = DATA_DIR / "wrong_data.csv"
    cleaned_file = DATA_DIR / "polarization_cleaned.csv"
    wrong_df = load_data(wrong_file)
    
    if wrong_df is None:
        st.info("No wrong data file found.")
    else:
        # Overview Grid
        with st.container(border=True):
            st.subheader("Data Cleaning Summary")
            try:
                # The pipeline preserves length by converting bad data to NaNs, so length == raw 
                total_raw = len(pd.read_csv(cleaned_file, usecols=[0]))
                anomalous_rows = len(wrong_df)
                clean_rows = total_raw - anomalous_rows
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Raw Data", f"{total_raw / 1e6:.2f} M")
                col2.metric("Bad Data Removed", f"{anomalous_rows / 1e6:.2f} M")
                col3.metric("Clean Data Used", f"{clean_rows / 1e6:.2f} M")
                
            except Exception:
                st.metric("Total Imputed Rows", f"{len(wrong_df) / 1e6:.2f} M")
                
        # Table Grid
        with st.container(border=True):
            st.subheader("Removed Anomalies")
            st.markdown("Displaying the first 1000 rows of anomalous `-99.990` records.")
            st.dataframe(wrong_df.head(1000), use_container_width=True)
        
        # ── NEW: Active (Clean) Data Matrix ──────────────────────────────────
        with st.container(border=True):
            st.subheader("📋 Active Clean Data Matrix")
            st.markdown("Showing the first **500 rows** of the clean, pipeline-filtered dataset used for all analysis.")
            try:
                clean_df_preview = pd.read_csv(cleaned_file, parse_dates=["timestamp"], nrows=500)
                
                # Column summary row
                cc1, cc2, cc3 = st.columns(3)
                cc1.metric("Columns", len(clean_df_preview.columns))
                cc2.metric("Rows Shown", len(clean_df_preview))
                cc3.metric("Date Range", f"{clean_df_preview['timestamp'].min().strftime('%b %d')} → {clean_df_preview['timestamp'].max().strftime('%b %d, %Y')}")
                
                st.dataframe(
                    clean_df_preview,
                    use_container_width=True,
                    height=350
                )
            except Exception as e:
                st.warning(f"Could not load clean data preview: {e}")
