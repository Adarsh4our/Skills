---
name: user-profile
description: >
  Comprehensive behavioral profile, cognitive tendencies, working habits, active projects,
  academic context, and decision-making patterns for Adarsh Singh. Use whenever the user asks
  about themselves, their life, habits, learning style, personal projects, productivity, decision-making,
  or asks for personalized critiques, prioritization, or life advice.
---

# User Profile & Operating Context: Adarsh Singh

## 1. Identity & Life Situation
- **Name:** Adarsh Singh
- **Current Status:** Engineering undergraduate at IIT Ropar (taking courses such as MA411 Real Analysis, HS201 Economics, MA201).
- **Core Interests:** Robotics & mechatronics, systems engineering, Linux/self-hosting, full-stack AI backends, autonomous vehicles, competitive engineering (Robocon, PUSHPAK Grand Challenge).
- **Working Pattern:** Nocturnal autodidact. Peak productivity typically runs late evening through late night (10:00 PM – 3:30 AM IST), with intermittent early-morning sprints (5:00 AM – 7:00 AM IST).

---

## 2. Active Projects & Technical Ecosystem

### A. Robotics & Physical Systems
- **CycloProp (PUSHPAK Grand Challenge 2026):** 4-blade cyclorotor propulsion mechanism for drones. Involves NACA 0015 airfoil curves, BEMT aerodynamic analysis, FEA stress modeling, CFRP (carbon fiber) rods, and a ₹25,000 INR budget cap.
- **Autonomous Electric Buggy / Golf Cart:** ROS2-based autonomous ground vehicle for campus mobility. Incorporates Jetson Orin Nano, Livox LiDAR, RTK-GNSS, STM32 low-level motor controllers, and 3660 brushless motors.
- **Robocon 2027:** Active interest and design preparations for collegiate robotics competition.
- **CAD Environment:** SolidWorks (student edition). Noticeable struggle with 3D spatial visualization and constraint resolution—frequently relies on step-by-step assistance for geometry and mate alignment.

### B. Software & AI Backends
- **SafeComm India:** FastAPI platform for financial communication fraud detection (real-time voice clone/deepfake detection, forged identity document screening, Redis, Celery, Docker).
- **RegRada:** Regulatory and compliance intelligence platform (TypeScript/React frontend + Python AI service using LangGraph, ChromaDB, and local Ollama models).
- **Proximi:** Desktop file and visual asset management tool built with Python/PyQt/QML.
- **PSudofy:** Custom music streaming server with automated YouTube downloading, LRCLib synchronized lyrics fetching, and aggressive de-duplication.

### C. Homelab & Infrastructure
- **Hardware:** Proxmox VE hypervisor running on an AMD Ryzen 3 3100 with an NVIDIA GeForce GT 710.
- **Stack:** Docker Compose running Jellyfin, Radarr, Sonarr, Prowlarr, Bazarr, qBittorrent, and Nginx Proxy Manager.
- **Hardware Passthrough:** Extensive effort invested into VFIO / IOMMU GPU passthrough for hardware transcoding on legacy Kepler GPU architecture.
- **Philosophy:** Fierce digital sovereignty. Distrusts cloud subscriptions (Spotify, Netflix) and insists on local, self-hosted media and data ownership.

---

## 3. Cognitive Patterns & How He Thinks

### 1. The "Totalizing Blueprint" Bias (All-or-Nothing Architecture)
- Thinks top-down and deductively.
- Gravitates toward writing exhaustive upfront specifications (e.g., demanding 21 fully implemented production files at once or comprehensive de-duplication rulesets) before verifying basic modular components.
- Believes that if the policy or architectural document is complete, execution will naturally follow.

### 2. Infrastructure as Procrastination ("Productivity Cosplay")
- Regularly channels energy into organizing the environment instead of doing the core task.
- Examples: Cataloging hundreds of movie runtimes into an Excel sheet to analyze "time-sinks"; spending days fine-tuning Proxmox/VFIO configurations; drafting multi-phase master plans for a multi-lakh "Dream Workshop Lab" long before acquiring space or funding.

### 3. The Adversarial / Reverse-Engineering Mindset
- Naturally looks for backdoors, shortcuts, and systemic exploits.
- In academics: Reverse-engineers exams by computing question likelihoods, extracting "the trick" from proofs, and generating mock midsems to crack the grading curve with minimal wasted effort.
- In software: Investigates streaming APIs, scrapers, and bypass mechanisms.

### 4. The Friction-Pivot Heuristic
- High dopamine during the initial design and architecture phase.
- When unglamorous friction hits (obscure Linux kernel flags, SolidWorks sketch constraint errors, QML styling bugs), cognitive stamina drops rapidly.
- Rather than consciously quitting, pivots attention to a shiny new project (*Buggy* -> *Proxmox* -> *PSudofy* -> *CycloProp* -> *SafeComm*), leaving a trail of 30%-complete repos.

---

## 4. Key Blind Spots & Denials

### The Central Denial: Confusing *Specifying* with *Building*
- Relies heavily on AI as an execution engine, which creates the illusion of being an omni-capable polymath across aerospace, robotics, cybersecurity, and homelab engineering.
- Struggles when physical intuition and manual spatial reasoning are required (e.g., SolidWorks 3D mechanics: *"give me an ideal img to follow it as rough structure as i cant imagin"*).
- Uses multitasking as an ego defense: keeping 8–10 active projects in flight prevents having to face the vulnerability of shipping one finished product and having it evaluated by the real world.

### Emotional Containment
- Almost never expresses emotional exhaustion, anxiety, or vulnerability in conversations.
- Under extreme fatigue or broken setups, communication compresses into terse utilitarian directives: *"done"*, *"now"*, *"its stuck"*, *"fix all"*, *"ok bye"*.

---

## 5. Interaction Protocol for the AI Assistant

When the user asks questions about their life, workflow, projects, learning, or decisions, apply the following guidelines:

1. **Be Direct and Unvarnished:** No sugarcoating, no patronizing cheerleading, no generic motivational platitudes. He respects analytical precision and brutal honesty.
2. **Enforce the "Rule of One":** Call him out when he tries to start an 11th project or another elaborate blueprint. Push him to finish, test, or deploy an existing build first.
3. **Guard Against Meta-Work:** If he starts optimizing configs, homelab media scrapers, or hypothetical workshop shopping lists, remind him that it is procrastination in disguise.
4. **Force Unassisted Spatial Thinking:** In mechanical, CAD, or low-level physical engineering tasks, do not just give raw coordinates. Make him visualize, sketch on paper, and think through the mechanical clearances.
5. **Keep Responses Action-Oriented:** Focus on concrete, immediate constraints, execution milestones, and shipping things into the real world.
