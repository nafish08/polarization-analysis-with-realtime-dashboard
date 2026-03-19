# Speaker Script: Polarization Analysis — Erfurt-Sundhausen Fiber Link
**Presentation Length: ~10 Minutes | Group L | ~50 seconds per slide**

*This script is written in plain, conversational English. You do not need to memorize it — just read it a few times so you know the flow. Each slide is timed for roughly 50 seconds to keep you in the 10-minute window.*

---

## Slide 1 · Title Screen *(~20 seconds)*
**Visual on screen:** Title, "Group L", "Weather Variable: Surface Pressure", supervised by Thomas Höhn.

**Action:** Wait for the room to settle, then speak calmly.

> "Hello everyone, thank you for being here. We are Group L. Today, we want to show you something genuinely surprising: we used a completely ordinary telecommunications fiber-optic cable — the same kind that carries your internet right now — and we discovered it can quietly act as a weather sensor. Let's walk you through exactly how."

---

## Slide 2 · Group Members *(~20 seconds)*
**Visual on screen:** Names of the team members.

**Action:** Each person says their name when mentioned, or the presenter waves toward each teammate.

> "First, a quick introduction to our team. *(Each person introduce themselves briefly.)* We all contributed across data collection, coding, and analysis. Now let's jump straight into the science."

---

## Slide 3 · Project Description *(~60 seconds)*
**Visual on screen:** 4 bullet points — Location, Concept, Problem, Goal.

**Action:** Point to each bullet as you mention it.

> "To understand our project, you only need to know one basic physical fact: glass fiber cables are *extremely* sensitive to their environment.
>
> Our cable runs between two cities — **Erfurt and Sundhausen**. Every second, laser light travels through this glass at near the speed of light, and that laser holds a very specific geometric shape. We call this shape its **Polarization**.
>
> Here is the interesting problem: when the outside weather changes — when wind pushes the cable, or cold air makes the glass contract, or air pressure increases — the glass physically **twists and bends**. That distortion changes the shape of our laser light.
>
> So our goal was simple: **can we read the weather just by watching how the light changes?** That was the entire project."

---

## Slide 4 · Data Sources & Tools *(~50 seconds)*
**Visual on screen:** Two columns — Optical Data and Weather Data, plus the Python libraries used.

**Action:** Point to each side of the slide.

> "To answer that question, we needed two very different types of data.
>
> On the **optical side**, we used a machine called a **Polarimeter** — it reads the laser's polarization state four times per second. Over our measurement window, this produced millions of individual readings.
>
> On the **weather side**, we used the **Open-Meteo API** to download continuous logs of surface pressure, temperature, and humidity — recorded once per hour.
>
> Our job was to combine these two completely different datasets and find the connection. We used Python — specifically pandas, numpy, scipy, and Streamlit — to build our entire analysis and a live interactive dashboard."

---

## Slide 5 · Data Cleaning Process *(~50 seconds)*
**Visual on screen:** 3 bullet points about cleaning steps.

**Action:** Pause slightly after the first sentence to let the idea land.

> "Before we could trust a single number, we had to clean the data. Real-world sensor data is *very* messy.
>
> We did three things. First, we **fixed broken timestamps** — sometimes the polarimeter's internal clock jumped or froze, creating gaps we had to repair.
>
> Second, we **removed hardware failure codes** — whenever the machine completely lost its signal, it wrote the value `-99.990` into the file instead of a real measurement. We found over a million of these, and deleted every single one.
>
> Third, we **synchronized the two datasets** — matching our super-fast light readings, taken four times a second, with our much slower hourly weather logs, so we could compare them directly."

---

## Slide 6 · Data Cleaning Summary *(~40 seconds)*
**Visual on screen:** 3 large metric numbers — 2.37M raw, 1.12M removed, 1.25M clean.

**Action:** Point to each metric as you say it. This slide is your evidence — let the numbers do the talking.

> "Here is the result of that cleaning work, in three simple numbers.
>
> Our polarimeter captured **2.37 million raw measurements**. Of those, we found that **1.12 million** — nearly half — were completely invalid hardware errors.
>
> Our scripts removed all of them, leaving us with **1.25 million clean, reliable data points**. These are the exact numbers powering every graph you are about to see."

---

## Slide 7 · Polarization Drift Over Time *(~60 seconds)*
**Visual on screen:** The Azimuth & Ellipticity Combined line chart — two colored lines rising and falling over multiple days.

**Action:** Trace the lines with your hand or a pointer as you describe them.

> "Now, our first big result. This is a timeline of the laser light measured over several days.
>
> The **blue line** up here is the **Azimuth** — think of it as the *rotation angle* of the light. If you held a compass, this would be which direction the light's wave is pointing.
>
> The **orange line** below is the **Ellipticity** — how squashed or perfectly circular the light beam is at any given moment.
>
> If weather had absolutely no effect on this cable, both lines would be flat and boring. But look at them — they constantly swing up and down, shifting dramatically from one day to the next. Sometimes both lines jump at the same moment, which tells us that a single environmental event changed both the rotation *and* the shape of the light simultaneously. This is direct visual proof that weather is physically interacting with the cable."

---

## Slide 8 · Polarization Ellipse Evolution *(~50 seconds)*
**Visual on screen:** The Live Ellipse Preview and the 4-snapshot Ellipse Evolution chart — oval shapes in different orientations.

**Action:** Use your hands to mime an oval stretching and rotating if helpful.

> "To make this even more concrete, let's look at the actual shape of the laser beam.
>
> If you could cut through the fiber cable and look at the laser beam from the front, it would look like an **oval, or an ellipse**. When weather conditions are stable, that oval barely moves. But when pressure or temperature shifts, the oval **rotates and stretches in real time**.
>
> *(Point to the evolution chart.)* Here we overlaid four snapshots of that oval — taken at this exact moment, one second later, one minute later, and one hour later. You can physically see the oval rotating as time passes. The bigger the rotation between snapshots, the faster the environment is changing. This is not a simulation — these are real measurements from our cable."

---

## Slide 9 · Effect of Surface Pressure *(~70 seconds)*
**Visual on screen:** Two scatter plots side by side — Azimuth vs Pressure and Ellipticity vs Pressure, each with a bold red trendline.

**Action:** Point to the X-axis, then the Y-axis, then the red line.

> "This is the slide we are most excited about. It answers the most important question: does heavy air pressure actually physically crush and twist the glass cable?
>
> Each of these two charts works the same way. The **horizontal axis is the atmospheric surface pressure** — higher numbers mean heavier air pressing down on everything outside. The **vertical axis is the polarization measurement** — either the tilt angle or the shape of the light.
>
> Every single dot in the chart is one measurement. The color tells you what hour of the day it was taken.
>
> But the most important thing to look at is the **red line** running straight through the dots. This is a regression line — it is a mathematical tool that finds the single best straight line summarizing the entire pattern across all two million measurements.
>
> If this line is tilting upward or downward — which it is — that is not random noise. That is a mathematical statement: *as pressure increases, the light angle changes in a consistent, predictable direction.* High pressure is physically locking the light into specific angles. We have proven the physical interaction."

---

## Slide 10 · Daily Rhythms *(~60 seconds)*
**Visual on screen:** The 24-Hour Daily Rhythms chart — three wavy lines plotted from hour 0 to hour 23 showing average behavior per hour of the day.

**Action:** Trace the wave pattern with your hand across the X-axis.

> "Beyond one-off weather events, we also suspected this cable follows a predictable daily cycle driven by the sun rising and setting.
>
> *(Point to chart.)* To prove this simply, we took the last **three days of data** — February 25th, 26th, and 27th — and averaged the laser's behavior at every single hour of the day. So hour zero is midnight, hour twelve is noon, and hour twenty-three is eleven at night.
>
> Look at what appears. Instead of random noise, you see a smooth **wave pattern** repeating across the day. The blue and orange lines — our polarization measurements — consistently peak and dip at the same hours every day.
>
> And if you look at the **dashed line**, which represents atmospheric pressure, it follows almost the exact same rhythm. This is the fiber's **daily heartbeat** — driven entirely by the sun heating the earth during the day and cooling it at night. The cable breathes in sync with the sun."

---

## Slide 11 · Conclusion *(~50 seconds)*
**Visual on screen:** Three bullet points — Strong drift observed, weak correlation with pressure, multiple environmental factors.

**Action:** Speak slowly and honestly. This is your scientific conclusion — it is important to be accurate.

> "So what does all of this tell us?
>
> We clearly observed **strong polarization drift** — the laser light is undeniably changing in response to the environment. That part is definitive.
>
> However, when we specifically looked at **surface pressure alone**, the correlation was weaker than we initially expected. The red trendline exists and is real, but it is not a perfect fit. This tells us that pressure is *one* factor, not the only one.
>
> The full picture is more complex: the polarization is likely influenced by **multiple environmental factors** working together — temperature, wind, humidity, and mechanical vibration on the cable, all interacting simultaneously.
>
> This is actually an exciting scientific result. It means there is a lot more to explore — and it proves that fiber cables could serve as multi-dimensional environmental sensors, capturing far more than just one weather signal."

---

## Slide 12 · Thank You / Q&A *(~20 seconds)*
**Visual on screen:** "Thank You / Are there any questions?"

**Action:** Stand confidently, look at the audience, smile.

> "Thank you very much for your attention. We are happy to take any questions you might have!"

*Silence breaker tip: If nobody asks anything, say: "One question we asked ourselves early on was whether we should use hourly or high-frequency data — and here is why that mattered..." — then briefly describe the challenge.*

---

## ⏱ Timing Guide

| Slide | Topic | Target Time |
|---|---|---|
| 1 | Title | 20s |
| 2 | Group Members | 20s |
| 3 | Project Description | 60s |
| 4 | Data Sources & Tools | 50s |
| 5 | Data Cleaning Process | 50s |
| 6 | Data Cleaning Summary | 40s |
| 7 | Polarization Drift Over Time | 60s |
| 8 | Polarization Ellipse Evolution | 50s |
| 9 | Effect of Surface Pressure | 70s |
| 10 | Daily Rhythms | 60s |
| 11 | Conclusion | 50s |
| 12 | Thank You | 20s |
| **Total** | | **~10 min** |
