import re

with open('dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Azimuth & Ellipticity Combined (Tab 1)
# Remove the old expander block.
content = re.sub(
    r'\s+with st\.expander\("ℹ️ Graph Explanation"\):\s+st\.markdown\("\*\*What does this show\?\*\*(.*?)twisted the fiber optic cable\."\)',
    '',
    content,
    flags=re.DOTALL
)
# Inject the info column at the top of the container
# Actually, the container starts with: `fig_comb = px.line(df_melted, ...)`
# Let's just find `st.plotly_chart(fig_comb, use_container_width=True, config=DL_CONFIG)`
# and put `st.markdown("...", help="...")` right before it!
content = content.replace(
    'st.plotly_chart(fig_comb, use_container_width=True, config=DL_CONFIG)',
    'st.markdown("ℹ️ **Hover for Physics Logic**", help="**What does this show?**\\nOverlaying both Azimuth (rotation angle) and Ellipticity (shape) over time.\\n\\n**Why does it matter?**\\nSeeing them on the same timeline reveals if severe rotation perfectly correlates with geometric shape distortion. If both lines jump or shift simultaneously, a massive external physical force (like air pressure or wind) simultaneously crushed and twisted the fiber optic cable.")\n            st.plotly_chart(fig_comb, use_container_width=True, config=DL_CONFIG)'
)

# 2. Welch's Periodogram (Tab 1)
content = re.sub(
    r'\s+with st\.expander\("ℹ️ Graph Explanation"\):\s+st\.markdown\("\*\*What does this show\?\*\*(.*?)sun and daily weather rhythm\."\)',
    '',
    content,
    flags=re.DOTALL
)
content = content.replace(
    'st.plotly_chart(fig_psd, use_container_width=True, config=DL_CONFIG)',
    'st.markdown("ℹ️ **Hover for Physics Logic**", help="**What does this show?**\\nBreaks the complex laser signal down into pure repeating frequencies. The X-axis represents cycles per day.\\n\\n**Why does it matter?**\\nA massive spike on the \'1 cycle/day\' mark mathematically proves the fiber optical cable has a 24-hour heartbeat synced entirely to the sun and daily weather rhythm.")\n                st.plotly_chart(fig_psd, use_container_width=True, config=DL_CONFIG)'
)

# 3. Azimuth vs Pressure (Tab 2)
content = re.sub(
    r'\s+with st\.expander\("ℹ️ Graph Explanation"\):\s+st\.markdown\("\*\*What does this show\?\*\*(.*?)cable in a repeating pattern\."\)',
    '',
    content,
    flags=re.DOTALL
)
content = content.replace(
    'st.plotly_chart(fig_s_az, use_container_width=True, config=DL_CONFIG)',
    'st.markdown("ℹ️ **Hover for Physics Logic**", help="**What does this show?**\\nMaps the laser\'s physical rotation against the weather\'s atmospheric surface pressure.\\n\\n**Why does it matter?**\\nThis directly proves causation. If the dots form a distinct upward or downward correlation line across the grid, it proves that rising outdoor pressure specifically twists the glass cable in a repeating pattern.")\n                    st.plotly_chart(fig_s_az, use_container_width=True, config=DL_CONFIG)'
)

# 4. Ellipticity vs Pressure (Tab 2)
content = re.sub(
    r'\s+with st\.expander\("ℹ️ Graph Explanation"\):\s+st\.markdown\("\*\*What does this show\?\*\*(.*?)geometry containing your data stream\."\)',
    '',
    content,
    flags=re.DOTALL
)
content = content.replace(
    'st.plotly_chart(fig_s_el, use_container_width=True, config=DL_CONFIG)',
    'st.markdown("ℹ️ **Hover for Physics Logic**", help="**What does this show?**\\nMaps how \'squashed\' the laser beam gets compared to the weather\'s atmospheric surface pressure.\\n\\n**Why does it matter?**\\nJust like above, seeing a trend here proves the environmental weight of the air physically crushes the microscopic glass geometry containing your data stream.")\n                    st.plotly_chart(fig_s_el, use_container_width=True, config=DL_CONFIG)'
)

# 5. Drift Chart Matplotlib (Tab 3)
content = re.sub(
    r'\s+with st\.expander\("ℹ️ Graph Explanation"\):\s+st\.markdown\("\*\*What does this show\?\*\*(.*?)twisting apart in real-time\."\)',
    '',
    content,
    flags=re.DOTALL
)
# Modify title to include columns and download button
drift_target = r'st\.markdown\("\*\*Drift in Parameter Space\*\*"\)'
drift_replace = '''col_title, col_btns = st.columns([0.85, 0.15])
                        with col_title:
                            st.markdown("**Drift in Parameter Space**")
                        with col_btns:
                            st.markdown("ℹ️ [Hover]", help="**What does this show?**\\nMaps the entire Azimuth vs Ellipticity collision boundary over the entire selected block. Color indicates the progression of time forward.\\n\\n**Why does it matter?**\\nA tight circle block means the laser is stable. If the dots streak wildly or shift entirely across the geometric map, the fiber is actively twisting apart in real-time.")'''
content = re.sub(drift_target, drift_replace, content)

# Modify download button to inject into col_btns safely
dl_drift_target = r'st\.download_button\(label="📸 Download Drift Chart \(\.jpg\)", data=buf_drift\.getvalue\(\), file_name="drift_parameter_space\.jpg", mime="image/jpeg", use_container_width=True\)'
dl_drift_replace = r'st.download_button(label="📸 DL", data=buf_drift.getvalue(), file_name="drift_parameter_space.jpg", mime="image/jpeg", key="dl_drift")'
content = content.replace(dl_drift_target, dl_drift_replace)

# 6. Live Ellipse Preview (Tab 3)
content = re.sub(
    r'\s+with st\.expander\("ℹ️ Graph Explanation"\):\s+st\.markdown\("\*\*What does this show\?\*\*(.*?)environmental pressure outside the glass\."\)',
    '',
    content,
    flags=re.DOTALL
)
ell_target = r'st\.markdown\("\*\*Live Ellipse Preview\*\*"\)'
ell_replace = '''col_title2, col_btns2 = st.columns([0.85, 0.15])
                        with col_title2:
                            st.markdown("**Live Ellipse Preview**")
                        with col_btns2:
                            st.markdown("ℹ️ [Hover]", help="**What does this show?**\\nA literal 2D geometric cross-section of the laser beam at the exact split-second `t` you locked on the slider.\\n\\n**Why does it matter?**\\nYou are physically seeing the real-time optical shape of the beam being warped by external environmental pressure outside the glass.")'''
content = re.sub(ell_target, ell_replace, content)

dl_ell_target = r'st\.download_button\(label="📸 Download Ellipse Image \(\.jpg\)", data=buf_ell\.getvalue\(\), file_name="live_ellipse_preview\.jpg", mime="image/jpeg", use_container_width=True\)'
dl_ell_replace = r'st.download_button(label="📸 DL", data=buf_ell.getvalue(), file_name="live_ellipse_preview.jpg", mime="image/jpeg", key="dl_ell")'
content = content.replace(dl_ell_target, dl_ell_replace)

# 7. Evolution Graph (Tab 3)
content = re.sub(
    r'\s+with st\.expander\("ℹ️ Graph Explanation"\):\s+st\.markdown\("\*\*What does this show\?\*\*(.*?)thermal gradient of the sun\."\)',
    '',
    content,
    flags=re.DOTALL
)
evo_target = r'st\.markdown\("\*\*Polarization Ellipse Evolution \(t, t\+1s, t\+1m, t\+1h\)\*\*"\)'
evo_replace = '''col_title3, col_btns3 = st.columns([0.85, 0.15])
                    with col_title3:
                        st.markdown("**Polarization Ellipse Evolution (t, t+1s, t+1m, t+1h)**")
                    with col_btns3:
                        st.markdown("ℹ️ [Hover]", help="**What does this show?**\\nOverlays 4 completely separate cross-sections of the identical laser beam taken at 4 different moments in time (`t`, `1 sec later`, `1 min later`, `1 hr later`).\\n\\n**Why does it matter?**\\nBy stacking them, we can physically measure the *velocity* of the distortion. Rapid shifts indicate fast wind/pressure drops, while slow hourly shifts map perfectly to the thermal gradient of the sun.")'''
content = re.sub(evo_target, evo_replace, content)

dl_evo_target = r'st\.download_button\(label="📸 Download Evolution Graph \(\.jpg\)", data=buf_evo\.getvalue\(\), file_name="ellipse_evolution\.jpg", mime="image/jpeg", use_container_width=True\)'
dl_evo_replace = r'st.download_button(label="📸 DL", data=buf_evo.getvalue(), file_name="ellipse_evolution.jpg", mime="image/jpeg", key="dl_evo")'
content = content.replace(dl_evo_target, dl_evo_replace)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Regex AST override successfully wrote all custom UI icon logic to dashboard.py.")
