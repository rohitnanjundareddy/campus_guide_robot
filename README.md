# Campus Guide Robot (Corrie)

A social campus tour-guide robot built on the Misty II platform, designed to explore how an expressive robot can provide engaging, human-centered guidance in a university building. Corrie leads visitors along a scripted route to a chosen destination, narrating each stop with synchronized gestures (pointing, head tilts, waving) and holding conversations through a voice-driven interaction flow. Speech is transcribed with Google Speech-to-Text, and an LLM generates context-aware responses based on the robot’s current location. Navigation uses timed dead-reckoning; a Wizard-of-Oz fallback was used during development trials when the system didn’t behave as expected.

## Project Overview

**Repository**: https://github.com/rohitnanjundareddy/campus_guide_robot  
**Papers**: Research Paper (Corrie-ResearchPaper.pdf) and Design Paper (Corrie-DesignPaper.pdf)  
**Course**: CS 531 - Social Robotics & HRI, University of Illinois Chicago

This project explores how social robots can complement human help desks by handling routine wayfinding tasks while providing the same social supports users expect from human guides.

---

## System Architecture

Corrie is a Python controller that drives Misty II over its REST API. The prototype combines a voice-driven conversation loop with a scripted, gesture-rich tour route.

<div align="center">
<table><tr><td>
<pre>
┌──────────────────────────────────────────────────────────────┐
│              CORRIE: SOCIAL CAMPUS GUIDE ROBOT               │
│                          (Misty II)                          │
│                                                              │
│  ┌─ ROBOT DESIGN: Misty II hardware ──────────────────────┐  │
│  │ Inputs:  microphone, camera, depth / ToF sensors       │  │
│  │ Outputs: treads, arms, head, speaker, LCD face         │  │
│  └────────────────────────────────────────────────────────┘  │
│                               │ Python + Misty REST API      │
│                               ▼                              │
│  ┌─ SOFTWARE (Python) ────────────────────────────────────┐  │
│  │ Mic (3 s chunks) > Google Speech-to-Text > GPT-3.5     │  │
│  │ dialogue (prompted with tour location)                 │  │
│  │ Tour controller: state machine, threaded speech queues │  │
│  └────────────────────────────────────────────────────────┘  │
│                               │                              │
│                               ▼                              │
│  ┌─ INTERACTION (HRI) ──────┐  ┌─ NAVIGATION ─────────────┐  │
│  │ Voice-triggered start    │  │ Dead-reckoning: timed    │  │
│  │ Narration at each stop   │  │ drive + turns on a       │  │
│  │ Gaze: head turn / tilt   │  │ scripted route, stops at │  │
│  │ Gestures: point, wave    │  │ pantry, reception,       │  │
│  │ Asks visitors questions  │  │ posters, sandbox         │  │
│  └──────────────────────────┘  └──────────────────────────┘  │
│                               │                              │
│                               ▼                              │
│  ┌─ FALLBACK ─────────────────────────────────────────────┐  │
│  │ Wizard-of-Oz: human backup, only if needed             │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─ DESIGN GOALS ─────────────────────────────────────────┐  │
│  │ Satisfaction | Inclusion | Trust | Independence        │  │
│  │ A social guide that complements human help desks       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─ RESEARCH STUDY (CS 531) ──────────────────────────────┐  │
│  │ Robot guide vs. human help desk (within-subjects)      │  │
│  │ Measures: inclusion, independence, satisfaction, trust │  │
│  │ Methods: surveys, observation, interviews              │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
</pre>
</td></tr></table>
</div>

---

## Core Components

### 1. Navigation Pipeline

Corrie follows a scripted indoor route using timed dead-reckoning. Motion commands with fixed speeds and durations drive each straight segment and turn, and the robot pauses at set stops along the way to engage the visitor.

#### **1.1 Motion Control**
- **Locomotion**: Tread-based drive controlled through Misty's REST API (linear and angular velocity for a set duration)
- **Straight Segments**: Timed forward driving at a fixed speed
- **Turns**: Timed in-place rotation toward each landmark and back onto the route

#### **1.2 Scripted Route and Stops**
- **Route**: Fixed path with four stops on the robotics research lab floor: pantry, reception, research posters, and sandbox
- **At Each Stop**: Turns toward the landmark, orients its head, points with an arm, and narrates
- **Visitor Check-ins**: Pauses at the pantry and the poster display to ask the visitor a question, then continues after the response
- **Resume**: Re-centers its head and continues to the next segment

#### **1.3 Explored and Future Work**
The design paper describes a fuller navigation stack. Some of it was explored during development before the prototype settled on scripted navigation:
- **SLAM** *(explored)*: Mapping and pose tracking on Misty II for autonomous localization
- **Sensing** *(design only)*: Camera, time-of-flight, and depth sensors for obstacle detection and mapping
- **Landmark/Object Detection** *(design only)*: Map-pinned landmarks (reception desks, vending machines) combined with camera-based detection for posters
- **Path Planning** *(design only)*: Safe indoor routes with obstacle avoidance

---

### 2. Communication Pipeline

The communication pipeline handles Corrie's conversation with visitors. It listens continuously, transcribes speech, triggers each stage of the tour, and responds with scripted narration and LLM-generated replies.

#### **2.1 Speech Recognition**
- **Audio Capture**: Misty records short 3-second audio chunks through its microphone
- **Speech-to-Text**: Each chunk is transcribed with the Google Speech-to-Text API (English)
- **Continuous Listening**: Runs in a background thread so Corrie can hear visitors while it moves and speaks

#### **2.2 Dialogue System (LLM-Based)**
- **Model**: OpenAI GPT-3.5, used for short, friendly replies (1-2 sentences)
- **Location-Aware Context**: Each prompt includes where Corrie is on the tour (for example, near the pantry or at the research posters)
- **Where It Is Used**: Replies to the visitor's snack and field-of-interest answers, and responses to general comments during the tour
- **Fallback Responses**: Preset lines are used if the LLM request fails, so the tour is never interrupted

#### **2.3 Scripted Tour Narration**
- **Fixed Content**: Narration at each stop (pantry, reception, research posters, sandbox) is written in advance, so the facts Corrie shares are reliable
- **Visitor Questions**: Corrie asks what snack the visitor grabs when busy (at the pantry) and what their field of interest is (at the posters), then reacts to the answer
- **Why Scripted**: Pre-written narration keeps facts accurate and timing predictable, while the LLM adds personality in the conversational moments

#### **2.4 Voice-Triggered Interaction Flow**
A state machine moves the visitor through the start of the tour:
1. **Greeting**: The visitor says "hello" and Corrie greets them and asks where they would like to go
2. **Destination**: The visitor names the destination (the prototype supports the sandbox)
3. **Start**: The visitor says "let's start" and the tour begins
4. **During the Tour**: Corrie narrates each stop and pauses for the visitor's answers

#### **2.5 Robot Social Behaviors**
- **Speech Output**: Misty text-to-speech with a friendly, upbeat tone and progress remarks between stops
- **Gaze**: Head turns toward landmarks (left or right) and tilts while listening for an answer
- **Expressive Display**: Misty's LCD eyes and LED animations are used throughout the interaction to convey expression
- **Gestures**: Points with the left or right arm at landmarks, gestures forward when heading onward, and waves goodbye
- **Narration Timing**: Gestures are synchronized with speech at each stop

#### **2.6 Concurrent Speaking and Listening**
- **Speaking Thread**: Plays tour narration and LLM replies from two queues, with tour narration taking priority
- **Listening Thread**: Records, transcribes, and routes speech while the robot continues the tour
- **Shared State**: Flags track what the robot is waiting for (snack answer, interest answer), so a visitor's reply is routed to the right response

#### **2.7 Explored and Future Work**
- **RAG Campus Knowledge Base** *(explored)*: Retrieving campus information (landmarks, hours, help desks) to ground the LLM's answers; the prototype uses scripted narration instead
- **Language and Direction Detection** *(design only)*: Detecting the user's language and direction of speech, and focusing on one user at a time
- **Adaptive Expressions** *(design only)*: Eye and LED expressions that adapt to the visitor's reactions

---

## Design Principles

The design paper organizes Corrie around four core goals. Each goal is listed with how the current prototype supports it.

### **1. Satisfaction**
- Smooth, understandable, and pleasant interactions that leave visitors feeling supported
- Clear explanations, timely progress updates, and expressive feedback during guidance
- **In the prototype**: Narration at every stop, progress remarks between stops ("Let's keep moving forward!", "Almost there!"), and gestures synchronized with speech

### **2. Inclusion**
- An approachable, conversational style that welcomes students, staff, faculty, parents, and guests
- Campus context and landmark commentary that make visitors feel part of campus life
- **In the prototype**: A friendly greeting, light humor in the narration, and questions that invite the visitor into the conversation (favorite snack, field of interest)

### **3. Trust**
- Predictable behavior and consistent communication
- The robot explains what it is doing and what comes next
- **In the prototype**: Corrie announces each movement before making it ("Follow me down this hallway", "Now we're going to make a right turn here") and uses head turns and pointing to show where it is directing attention

### **4. Independence**
- Visitors choose between being escorted or receiving directions and continuing on their own
- Landmark-based guidance gives enough information to navigate without the robot
- **In the prototype**: This goal is a design target. The current prototype escorts visitors along the route and does not yet offer a directions-only mode

---

## Interaction Scenarios

### Implemented Tour Flow (Prototype)

The prototype runs one scripted tour from the entrance to the sandbox.

1. Corrie introduces itself: *"Greetings! I'm Corrie, your tiny robot guide! Say hello to get started!"*
2. The visitor says "hello". Corrie greets them and asks where they would like to go.
3. The visitor names the destination ("sandbox"). Corrie gestures ahead and asks them to say "let's start" when ready.
4. The visitor says "let's start" and the tour begins.
5. Corrie drives the route and stops to engage the visitor at each landmark:
   - **Pantry**: turns its head toward the pantry, points, and jokes about the coffee and snacks. It asks what the visitor likes to grab when busy, then replies to their answer with an LLM-generated comment.
   - **Reception**: turns toward the desk, points, and introduces Enrique, who works there.
   - **Research Posters**: points at the posters and shares a joke about a robotics professor's poster. It asks about the visitor's field of interest, then replies to their answer with an LLM-generated comment.
   - **Sandbox**: arrives, explains what the sandbox is used for, thanks the visitor, and waves goodbye.
6. Between stops, Corrie announces what it is about to do (*"Follow me down this hallway"*, *"Onward we go!"*) and answers general visitor comments using the LLM.

### Design Scenarios (from the design paper)

The design paper describes how Corrie would work in a full deployment. These scenarios go beyond the current prototype.

#### Scenario 1: Robot-Assisted Navigation
1. A visitor approaches the robot, or a help desk dispatches it
2. Corrie greets the visitor and offers to walk with them: *"Would you like me to walk with you there? I can point out some interesting spots along the way!"*
3. The visitor can accept or decline, which keeps the choice in their hands
4. During navigation, Corrie:
   - Points out landmarks, such as a reception desk
   - Comments on interesting features, such as a poster about the robotics club
   - Gives progress updates: *"We're about halfway there!"*
5. Corrie arrives at the destination and confirms completion

#### Scenario 2: Help Desk Integration
1. A visitor asks a human help desk for routine directions, for example to a classroom
2. The staff member recognizes this as a routine task and dispatches a robot guide
3. The robot approaches the visitor: *"Hi! I can walk with you to that classroom and show you some cool spots along the way."*
4. The staff member stays at the desk, available for complex questions from other visitors

#### Scenario 3: Landmark-Based Verbal Directions
1. A visitor prefers not to be accompanied
2. Corrie gives step-by-step directions using landmarks:
   - *"We'll head down this hallway and take a left at the vending machines up ahead."*
   - *"Once we turn left, we'll see the library entrance on the right."*
   - *"Our destination is just past the library, the third door on the left."*
3. The visitor navigates independently, with enough information to do so confidently

---

## Behavioral Mimicry of Human Guides

The design paper bases Corrie's behavior on how effective human guides help visitors. The table shows each behavior, how the robot approximates it, and whether it is in the current prototype.

| Human Guide Behavior | Robot Implementation | Status |
|---------------------|---------------------|--------|
| Stops at points of interest | Slows down and halts at each stop and turns toward the landmark | Prototype |
| Points at features | Left or right arm gesture toward the landmark | Prototype |
| Looks at what they are talking about | Head turns toward the landmark; head tilt while listening for an answer | Prototype |
| Shares information about the surroundings | Scripted narration at each stop | Prototype |
| Uses a friendly, upbeat tone | Misty text-to-speech with friendly, humorous scripted wording | Prototype |
| Gives reassurance and progress updates | Remarks between stops ("Let's keep moving forward!", "Almost there!") | Prototype |
| Engages in small talk | Questions to the visitor (favorite snack, field of interest) with LLM-generated replies | Prototype |
| Offers to walk with you or just give directions | Escorted or directions-only guidance, chosen by the visitor | Design only |
| Shares campus knowledge and history | LLM answers grounded in a campus knowledge base (RAG) | Explored |
| Keeps an appropriate distance | Path planning with social spacing | Design only |

---

## Hardware Platform: Misty II

**Platform**: Misty II Developer Robot, controlled over its REST API from a Python script on a laptop connected to the same network.

### **Used in the Prototype**

**Sensing**
- **Microphone**: Captures the visitor's speech in 3-second chunks for transcription

**Actuation**
- **Treads**: Tread-based drive for straight segments and turns
- **Head**: Articulated head for gaze (looking left or right, tilting while listening)
- **Arms**: Moveable arms for pointing and waving

**Expression and Output**
- **Speaker**: Text-to-speech for narration and replies
- **LCD Eyes and LEDs**: Eye expressions and LED animations used throughout the interaction

### **Available but Not Used in the Prototype**
- **Camera**: High-resolution camera for facial and object recognition
- **Time-of-Flight Sensors**: Distance sensing for obstacle detection
- **Depth Sensor**: 3D mapping, used for the SLAM attempt during development
- **Capacitive Touch Panels**: Simple physical interaction
- **Charging Dock Return**: Autonomous return to the dock for long-duration operation

---
 
## Software Stack

### **Primary Programming**
- **Language**: Python 3
- **Robot Control**: Misty II REST API, called over HTTP with the `requests` library (drive, arms, head, text-to-speech, and audio recording)
- **Speech Recognition**: Google Speech-to-Text API
- **Dialogue**: OpenAI GPT-3.5 for short, location-aware replies
- **Concurrency**: `threading` and `queue` for the listening and speaking threads

### **Dependencies**
- `requests`
- `openai`
- `google-generativeai`

### **Operation Modes**
- **Primary Mode**: Voice-triggered scripted tour
  - State machine: greeting, destination, "let's start", then the tour
  - Timed dead-reckoning navigation along a fixed route
  - Scripted narration, with LLM replies to the visitor's answers and comments
- **Fallback Mode**: Wizard-of-Oz (WoZ)
  - A human operator can take over if the system fails
  - Used during development trials; the main/final demo ran without it

--- 

## Research Foundation

This prototype accompanies a proposed mixed-methods study. The study has not been run with participants.

- **Research Question**: *How does interacting with a campus guide robot influence users' perceptions of inclusion, independence, satisfaction, and trust, compared to receiving assistance from human help desks?*

### Proposed Study Design
- **Methodology**: Mixed-methods (quantitative surveys + qualitative observation and interviews)
- **Participants**: College students and campus visitors, recruited until no new themes emerge (an expected 12-16 people)
- **Conditions**: Within-subjects design. Each participant is guided by both the robot and a human help desk assistant, in counterbalanced order, on identical navigation tasks
- **Data Collection**:
  - Pre- and post-interaction surveys (7-point Likert scales)
  - Observational notes (behavioral analysis)
  - Semi-structured interviews (thematic analysis)
- **Measures**:
  - Inclusion (Social Connectedness Scale)
  - Independence (capability and confidence items)
  - Satisfaction (enjoyment and utility)
  - Trust (reliability and understanding)
  - Warmth and competence (Godspeed questionnaire)
- **Analysis**:
  - Wilcoxon signed-rank tests comparing robot and human conditions
  - Thematic analysis of interviews and notes by two independent coders
- **Ethics**: Informed consent for audio and video recording, a visible indicator light while Misty records, and a full debrief about any Wizard-of-Oz control

---

## File Structure

```
campus_guide_robot/
├── campus_guide.py          # Main robot control script
├── papers/
│   ├── Corrie-ResearchPaper.pdf
│   └── Corrie-DesignPaper.pdf
└── README.md
```

---

## Key Features

- **Voice-triggered, state-machine tour flow** (hello, destination, "let's start")
- **Scripted route with timed dead-reckoning navigation**
- **Narration synchronized with gaze and gestures** (head turns, pointing, waving) at each stop
- **Expressive LCD eyes and LED animations**
- **LLM (GPT-3.5) replies** that use the robot's tour location as context
- **Visitor questions** with personalized responses (favorite snack, field of interest)
- **Multithreaded listening and speaking** with priority queues
- **Wizard-of-Oz fallback** available as a human backup

---

## Installation & Setup

### Requirements
- Python 3
- A Misty II robot on the same Wi-Fi network as your computer
- A Google Cloud API key with the Speech-to-Text API enabled
- An OpenAI API key

### Install Dependencies
```bash
pip install requests openai google-generativeai
```

### Configure
1. **Misty's IP address**: Set `MISTY_IP` in the `__main__` block of `campus_guide.py` to your robot's address (you can find it in the Misty app).
2. **API keys**: Store your keys as environment variables so they stay out of the repository:
```bash
export GOOGLE_API_KEY="your-google-key"
export OPENAI_API_KEY="your-openai-key"
```
Then read them in the `__main__` block:
```python
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
```

---

## Usage

1. Place Misty at the start of the route, facing down the hallway.
2. Run the script:
```bash
python campus_guide.py
```
3. Follow the voice prompts:
   - Say **"hello"** to activate Corrie
   - Say **"sandbox"** when asked where you would like to go
   - Say **"let's start"** to begin the tour
4. Answer Corrie's questions at the pantry and at the research posters when it asks.
5. Press `Ctrl+C` at any time to stop. Corrie re-centers its head, lowers its arms, and shuts down its threads.

### Notes
- **Route timings are tuned for one building.** Drive durations and turn times are fixed values in `execute_tour`. A different hallway or surface will need them re-measured (for example, `drive_forward(22, speed=80)` and the 2250 ms turns).
- **Dead-reckoning drifts.** Wheel slip and battery level change how far Misty actually travels, so check the starting position before each run.
- **Speak clearly and wait for Corrie to finish.** Audio is recorded in 3-second chunks, so overlapping speech may be missed.

---

## Future Enhancements

### From the Design Paper
- **SLAM-based autonomous navigation** *(explored)*: Replace timed dead-reckoning with mapping, localization, and sensor feedback
- **Landmark and object detection**: Map-pinned landmarks plus camera-based detection for posters and signage
- **Path planning and obstacle avoidance**: Safe indoor routes that adapt to people and obstacles
- **RAG campus knowledge base** *(explored)*: Ground the LLM's answers in campus information such as landmarks, hours, and help desk locations
- **Directions-only mode**: Let visitors choose between being escorted and receiving landmark-based directions, supporting the independence goal
- **Help desk dispatch**: Let help desk staff send a robot guide for routine wayfinding requests
- **Language and direction detection**: Detect the visitor's language and where they are speaking from, and focus on one user at a time
- **Adaptive expressions**: Eye and LED expressions that respond to the visitor's reactions

### Research
- **Run the proposed user study** comparing the robot with a human help desk assistant

### Additional Ideas
- **Multiple robots** stationed across campus buildings, as described in the design paper
- **Accessibility features** for visitors with visual or mobility impairments
- **Personalized recommendations**, with attention to the privacy concerns raised in the research paper

---

## Related Work & References

Full citations and discussion are in the papers. Key related work:

**Campus and public-space guide robots**
- Greenberg, Everett, Biswas (2024). *Development of a Socially Cognizant Robotic Campus Guide.* HRI '24.
- Hu et al. (2025). *NarraGuide: An LLM-Based Narrative Mobile Robot for Remote Place Exploration.* UIST '25.
- Kanda, Shiomi, Miyashita, Ishiguro, Hagita (2010). *A Communication Robot in a Shopping Mall.* IEEE Transactions on Robotics.

**Inclusion, trust, and privacy**
- Liu et al. (2024). *DRAGON: A Dialogue-Based Robot for Assistive Navigation With Visual Language Grounding.* IEEE Robotics and Automation Letters.
- Yu, Kasaei, Cao (2024). *PANav: Toward Privacy-Aware Robot Navigation via Vision-Language Models.* arXiv:2410.04302.
- Campagna and Rehm (2025). *A Systematic Review of Trust Assessments in Human-Robot Interaction.* ACM Transactions on Human-Robot Interaction.

**Research methods**
- Bartneck et al. (2024). *Introduction to Human-Robot Interaction: Social and Cognitive Empirical Methods.* Cambridge University Press.

---

## Acknowledgments

This work was completed as part of the CS 531 graduate course (Social Robotics & HRI) at the University of Illinois Chicago. We thank the course instructor and the university for providing access to the Misty II robot and campus spaces for development and testing.

---

## Authors

- **Vibha Suneel Navale** (vnava22@uic.edu)
- **Raksha Parag Pawar** (rpawa7@uic.edu)
- **Rohit Nanjundareddy** (rnanj@uic.edu)

**Institution**: University of Illinois Chicago (UIC)
**Course**: CS 531 - Social Robotics & HRI

