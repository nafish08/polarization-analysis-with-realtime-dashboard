# Speaker Script: Polarization Analysis Project (10 Minutes)

*(This script is written in very simple, conversational English. It is paced for about 1 minute per slide. You do not need to memorize it word-for-word, just use it as a comfortable guide!)*

---

### Slide 1: Title Screen
**Action:** Wait for the audience to settle down.
**Script:** 
"Hello everyone, thank you for being here today. My name is [Your Name], and presenting with me are [Partner 1] and [Partner 2]. Today we want to share a really exciting idea with you: We took a standard telecommunications fiber-optic cable, and we tested if we could use it as a massive, living weather sensor."

### Slide 2: Project Description
**Script:**
"To understand our project, you just need to know one basic rule: optical fibers are very physically sensitive. Our project focuses on a glass fiber cable hanging between Erfurt and Sundhausen. 

When laser light travels through this cable, the light holds a specific shape, which is called 'Polarization'. But here is the catch: when the outside weather changes—like when the wind pushes the cable or the air pressure drops—the glass fiber physically twists. Our main goal was to see if we could detect what the local weather was simply by looking at how the light was bending."

### Slide 3: Data Sources
**Script:**
"To test this, we needed two very different sets of data. 
First, we needed the optical data. We used a machine called a Polarimeter that reads the laser light incredibly fast—about four times every second. 
Second, we needed the real weather data to compare it to. We used the Open-Meteo API to download historical logs of the local air pressure, temperature, and humidity. Our main job was to combine these two huge sets of data into one."

### Slide 4: Cleaning the Data
**Script:**
"But in the real world, sensor data is very messy. 
Before we could make any graphs, we had to clean everything. We wrote Python scripts to fix broken timers. If our laser machine completely dropped a connection and just printed an error code like '-99.990', our code found those errors and deleted them.
Finally, we had to mathematically match our super-fast light readings with our much slower hourly weather updates so they could perfectly line up."

### Slide 5: Active Data Metrics
**Action:** Explain the screenshot from your Dashboard's Data Cleaning Summary.
**Script:**
"Here we can clearly see what the data cleaning pipeline accomplished. The physical polarimeter originally captured exactly 2.37 million raw measurements. 
However, when we analyzed the records, we found roughly 1.12 million measurements were completely broken or corrupted by hardware errors. 
Our scripts successfully filtered out all 1.12 million anomalous points, leaving us with a highly refined dataset containing 1.25 million perfectly clean, mathematically valid points. Those clean 1.25M points are exactly what powers all of the physics graphs you will see next."

### Slide 6: Tracking Light Over Time
**Action:** Point to the 'Azimuth & Ellipticity Combined' graph.
**Script:**
"Here is a timeline look at our laser light. 
The blue line is Azimuth—which is basically the 'tilt' angle of the light. The orange line is Ellipticity—which is how 'circular' the light beam is. 
If the weather had no effect, these would just be flat lines. But as you can see, they aggressively swing up and down over the days. This proves that the environment is constantly changing the light."

### Slide 7: Watching the Shape Change
**Action:** Point to your 'Live Ellipse Preview' purple graphic from your dashboard.
**Script:**
"If you actually visualize the physical light beam itself, it looks like an oval, or an ellipse. 
When the temperature or pressure changes outside, it forces that oval to stretch or rotate. We built a fully interactive dashboard that actually animates this exact movement in real-time, allowing us to watch the light physically react over the week."

### Slide 8: The Effect of Surface Pressure
**Action:** Point to the 'Azimuth vs Pressure Scatter' graphs from your dashboard.
**Script:**
"The most important question we had was: Does heavy atmospheric air pressure actually crush the glass cable?
This scatter plot compares the Air Pressure on the bottom to the Light Angles on the side. 
The answer is yes. As you move to the right where the pressure gets higher, you can visibly see all the dots cluster extremely tightly together. High pressure physically restricts the cable and locks the light into very specific angles."

### Slide 9: Discovering Daily Rhythms
**Action:** Point to the 'Welch's Periodogram' graph.
**Script:**
"Finally, beyond random weather, we strongly suspected the fiber was affected by the sun rising and setting every single day. 
To prove this, we used a fancy math tool called a Periodogram to hunt for repeating rhythms. 
Looking at the chart, you can clearly see a massive spike sitting exactly on the 24-hour frequency mark. This proves that the heating and cooling of the sun creates a daily heartbeat pulsing right through the fiber cable."

### Slide 10: Conclusion
**Script:**
"To conclude our findings: yes, standard commercial aerial communication fibers completely act like giant weather sensors. We have definitively proven that physical weather—specifically atmospheric phenomena like heavy air pressure—exerts enough physical force to significantly warp the internal geometry of the laser packets traveling inside the glass. 

By analyzing this data, we validated that we can theoretically turn the existing telecommunication cables already hanging above our heads into a massive environmental sensing network.

Thank you so much for your time and for listening to our presentation today. We would love to open the floor and answer any questions you might have!"
