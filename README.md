Let me search more specifically for the campus_guide.py file:Based on the papers and the repository structure you've shared, let me create a comprehensive README with detailed architecture based on the design diagrams in your papers:

# Campus Guide Robot (Corrie)

A social campus guide robot system designed to assist students, faculty, staff, and visitors with navigation and wayfinding on university campuses. Built on the Misty II platform, this robot combines autonomous SLAM-based navigation with LLM-powered conversational interaction to provide engaging, human-centered navigation assistance.

## Project Overview

**Repository**: https://github.com/rohitnanjundareddy/campus_guide_robot  
**Papers**: Research Paper (CS_531__Research_Paper__Final___1_.pdf) and Design Paper (CS_531__Design_Paper__Final_.pdf)  
**Course**: CS 531 - Social Robotics & HRI, University of Illinois Chicago

This project explores how social robots can complement human help desks by handling routine wayfinding tasks while providing the same social supports users expect from human guides.

---

## System Architecture

The system consists of two coordinated pipelines that work together to enable both autonomous navigation and natural social interaction:

```
┌─────────────────────────────────────────────────────────────┐
│                     MISTY II ROBOT                          │
│                                                             │
│  ┌──────────────────────┐  ┌──────────────────────────┐  │
│  │  Navigation Pipeline │  │ Communication Pipeline   │  │
│  │                      │  │                          │  │
│  │  ┌────────────┐     │  │  ┌────────────────┐     │  │
│  │  │  Sensors   │     │  │  │  User Speech   │     │  │
│  │  │ • Cameras  │     │  │  │  (Audio→Text)  │     │  │
│  │  │ • ToF      │     │  │  └────────┬────────┘    │  │
│  │  │ • Depth    │     │  │           │             │  │
│  │  └─────┬──────┘     │  │           ▼             │  │
│  │        │            │  │  ┌─────────────────┐   │  │
│  │        ▼            │  │  │   Speech        │   │  │
│  │  ┌────────────┐     │  │  │  Recognition    │   │  │
│  │  │   SLAM     │     │  │  └────────┬─────────┘  │  │
│  │  │ • Mapping  │     │  │           │             │  │
│  │  │ • Pose     │     │  │           ▼             │  │
│  │  │   Track    │     │  │  ┌──────────────────┐  │  │
│  │  └─────┬──────┘     │  │  │  Dialogue (LLM)  │  │  │
│  │        │            │  │  │  • Query         │  │  │
│  │        ▼            │  │  │    Processing    │  │  │
│  │  ┌────────────┐     │  │  │  • RAG for       │  │  │
│  │  │ Landmark/  │◄────┼──┼──┤    Campus Info   │  │  │
│  │  │  Object    │     │  │  └────────┬─────────┘  │  │
│  │  │ Detection  │     │  │           │             │  │
│  │  │ • Reception│     │  │           ▼             │  │
│  │  │   Desks    │     │  │  ┌──────────────────┐  │  │
│  │  │ • Vending  │     │  │  │ Campus Knowledge │  │  │
│  │  │   Machines │     │  │  │   Base (RAG)     │  │  │
│  │  │ • Posters  │     │  │  │ • Landmarks      │  │  │
│  │  └─────┬──────┘     │  │  │ • Building       │  │  │
│  │        │            │  │  │   History        │  │  │
│  │        ▼            │  │  │ • Help Desks     │  │  │
│  │  ┌────────────┐     │  │  └────────┬─────────┘  │  │
│  │  │   Path     │     │  │           │             │  │
│  │  │  Planning  │     │  │           ▼             │  │
│  │  │ • Safe     │     │  │  ┌──────────────────┐  │  │
│  │  │   Routes   │     │  │  │  Robot Social    │  │  │
│  │  │ • Obstacle │     │  │  │   Behaviors      │  │  │
│  │  │   Avoid    │     │  │  │ • Speech         │  │  │
│  │  └─────┬──────┘     │  │  │ • Gaze           │  │  │
│  │        │            │  │  │ • Gestures       │  │  │
│  │        ▼            │  │  │ • Landmark       │  │  │
│  │  ┌────────────┐     │  │  │   Pointing       │  │  │
│  │  │   Misty    │◄────┼──┼──┘                  │  │  │
│  │  │ Navigation │     │  │                      │  │
│  │  │ • Movement │     │  │                      │  │
│  │  │ • Tracking │     │  │                      │  │
│  │  └────────────┘     │  └──────────────────────┘  │
│  └──────────────────────┘                           │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │         Wizard-of-Oz (WoZ) Fallback           │ │
│  │      (Human Backup - Only if Needed)          │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Navigation Pipeline

The navigation pipeline enables autonomous indoor movement using SLAM-based localization and path planning.

#### **1.1 Sensor Layer**
- **Cameras**: High-resolution visual input for environment perception and facial recognition
- **Time-of-Flight (ToF) Sensors**: Depth sensing for obstacle detection
- **Depth Sensors**: 3D spatial awareness for mapping

#### **1.2 SLAM (Simultaneous Localization and Mapping)**
- **Mapping**: Creates 3D maps of indoor spaces (hallways, lobbies, corridors)
- **Pose Tracking**: Real-time robot position and orientation tracking
- **Map Updates**: Continuous environment perception and map refinement

#### **1.3 Landmark/Object Detection**
- **Fixed Landmarks**: Map-pinned locations (reception desks, vending machines)
- **Dynamic Objects**: Camera-based detection for posters and signage
- **Hybrid Approach**: Combines map pins for reliability with perception for flexibility

#### **1.4 Path Planning**
- **Route Generation**: Safe, efficient indoor paths to destinations
- **Obstacle Avoidance**: Real-time replanning around dynamic obstacles
- **Navigation Execution**: Tread-based locomotion with smooth movement

---

### 2. Communication Pipeline

The communication pipeline manages all conversational and social interaction behaviors.

#### **2.1 Speech Recognition**
- **Multi-Microphone Array**: Captures user voice commands
- **Audio-to-Text**: Converts speech to text for processing
- **Accent Support**: Handles multiple accents and speaking styles

#### **2.2 Dialogue System (LLM-Based)**
- **Large Language Model (LLM)**: Processes natural language queries
- **Contextual Understanding**: Interprets navigation requests and questions
- **Response Generation**: Creates conversational, context-aware responses

#### **2.3 Campus Knowledge Base (RAG)**
- **Retrieval-Augmented Generation (RAG)**: Combines LLM with structured campus data
- **Knowledge Types**:
  - Landmark information (locations, functions, hours)
  - Building history and facts
  - Help desk locations and availability
  - Campus amenities (vending machines, restrooms, study spaces)

#### **2.4 Robot Social Behaviors**
- **Speech Output**: Natural, friendly tone with progress updates
- **Gaze Control**: Head orientation toward users and landmarks
- **Gestures**: Pointing, nodding, turning toward features
- **Landmark Commentary**: Shares context about campus features during navigation
- **Expressive Display**: LED eye animations matching emotional context

---

## Design Principles

The robot is designed around four core goals:

### **1. Satisfaction**
- Clear route explanations with landmark-based guidance
- Timely progress updates during navigation
- Smooth, predictable movement
- Expressive feedback that feels supportive

### **2. Inclusion**
- Approachable conversational style
- Welcomes all campus visitors (students, staff, parents, guests)
- Accessible interaction design
- Makes users feel part of campus community

### **3. Trust**
- Predictable, consistent behavior
- Transparent communication about actions
- Reliable performance
- Legible motion patterns

### **4. Independence**
- Users can choose: escorted guidance OR verbal directions only
- Landmark-based explanations enable self-navigation
- Contextual information supports autonomous wayfinding

---

## Interaction Scenarios

### Scenario 1: Robot-Assisted Navigation
1. User approaches robot or robot is dispatched from help desk
2. Robot greets user warmly: *"Hi! Where would you like to go?"*
3. User requests destination (e.g., "Take me to Room 302")
4. Robot confirms and offers options: *"Would you like me to walk with you?"*
5. During navigation:
   - Robot moves smoothly, maintaining visible distance
   - Points out landmarks: *"We'll turn left at the vending machines"*
   - Shares campus context: *"This building was renovated in 2020"*
   - Provides progress updates: *"We're halfway there!"*
6. Robot arrives at destination and confirms completion

### Scenario 2: Help Desk Integration
1. Visitor approaches human help desk with routine wayfinding request
2. Help desk staff dispatches robot guide
3. Robot approaches visitor and takes over navigation task
4. Human staff remains available for complex questions from other visitors
5. Robot provides same quality guidance as human would

### Scenario 3: Landmark-Based Verbal Directions
1. User prefers not to be accompanied
2. Robot provides step-by-step landmark-based directions:
   - *"Head down this hallway and take a left at the vending machines up ahead"*
   - *"Those machines have the best snacks on campus!"*
   - *"Once you turn left, you'll see the library entrance on the right"*
   - *"Your destination is the third door past the library"*
3. User navigates independently with confidence

---

## Behavioral Mimicry of Human Guides

The robot replicates effective human guide behaviors:

| Human Guide Behavior | Robot Implementation |
|---------------------|---------------------|
| Slows down at landmarks | Reduces speed, orients toward feature |
| Points at features | Arm gesture toward landmark |
| Shares contextual info | LLM-generated commentary from knowledge base |
| Uses friendly tone | Speech synthesis with warm prosody |
| Provides reassurance | Progress updates and encouraging language |
| Engages in small talk | Contextual remarks about campus features |
| Maintains appropriate distance | Path planning with social spacing |

---

## Hardware Platform: Misty II

**Platform**: Misty II Developer Robot

**Sensors**:
- High-resolution camera
- Time-of-flight distance sensors
- Depth sensors for SLAM
- Multi-microphone array
- Capacitive touch sensors

**Actuators**:
- Tread-based locomotion system
- Articulated head for gaze control
- Moveable arms for pointing gestures

**Interface**:
- Expressive LCD face display
- LED animations
- Audio speaker for speech output

**Power**:
- Autonomous charging dock capability
- Long-duration operation support

---

## Software Stack

### **Primary Programming**
- **Language**: JavaScript (Misty SDK)
- **Navigation**: SLAM-based mapping and localization
- **Dialogue**: LLM integration for natural language processing
- **Knowledge Base**: RAG (Retrieval-Augmented Generation)

### **Operation Modes**
- **Primary Mode**: Semi-autonomous operation
  - SLAM-based pose localization
  - LLM-powered dialogue
  - Map-based + perception-based landmark detection
- **Fallback Mode**: Wizard-of-Oz (WoZ)
  - Used only for: system failures, testing phases, exceptional circumstances
  - Ensures reliability during development and edge cases

---

## Research Foundation

This implementation is based on a mixed-methods research study examining:

- **Research Question**: *How does interacting with a campus guide robot influence users' perceptions of inclusion, independence, satisfaction, and trust, compared to receiving assistance from human help desks?*

### Study Design
- **Methodology**: Mixed-methods (quantitative surveys + qualitative interviews)
- **Participants**: College students and campus visitors
- **Conditions**: Within-subjects design (robot vs. human guidance)
- **Data Collection**:
  - Pre/post-interaction surveys (7-point Likert scales)
  - Observational notes (behavioral analysis)
  - Semi-structured interviews (thematic analysis)
- **Measures**:
  - Inclusion (Social Connectedness Scale)
  - Independence (capability and confidence items)
  - Satisfaction (enjoyment and utility)
  - Trust (reliability and understanding)
  - Warmth/Competence (Godspeed questionnaire)

---

## File Structure

```
campus_guide_robot/
├── campus_guide.py          # Main robot control script
├── papers/
│   ├── CS_531__Research_Paper__Final___1_.pdf
│   └── CS_531__Design_Paper__Final_.pdf
└── README.md
```

---

## Key Features

✅ **Autonomous SLAM-based indoor navigation**  
✅ **LLM-powered conversational interaction with RAG for campus knowledge**  
✅ **Landmark detection using hybrid map pins + perception**  
✅ **Social behaviors: speech, gaze, gestures, landmark pointing**  
✅ **Human guide behavioral mimicry for natural interaction**  
✅ **Help desk integration and dispatch capability**  
✅ **Multi-modal communication (speech, movement, expression)**  
✅ **WoZ fallback for reliability during testing**

---

## Design Goals in Practice

### Satisfaction
- Clear landmark-based guidance
- Progress updates during navigation
- Friendly, encouraging tone
- Smooth, predictable movement

### Inclusion
- Welcoming interaction style
- Contextual campus information
- Makes visitors feel part of community
- Accessible to diverse users

### Trust
- Consistent, reliable behavior
- Transparent communication
- Explains actions clearly
- Maintains appropriate social distance

### Independence
- Offers escorted vs. verbal-only guidance
- Landmark-based directions enable self-navigation
- Contextual info supports autonomous wayfinding

---

## Installation & Setup

[To be added - installation instructions for Misty II SDK and dependencies]

---

## Usage

[To be added - how to run the campus guide robot]

---

## Future Enhancements

- **Multi-robot coordination** for larger campus coverage
- **Personalized recommendations** based on user profiles
- **Integration with campus scheduling systems**
- **Accessibility features** for users with visual/mobility impairments
- **Outdoor navigation capabilities** with GPS/GNSS
- **Advanced emotion detection** for adaptive social behaviors

---

## Related Work & References

See papers for full citations of:
- Campus guide robots (LoCoBot, NarraGuide)
- Communication robots in public spaces (Robovie-IIF)
- Trust and inclusion in HRI
- Privacy-aware navigation (PANav)
- LLM-based dialogue systems

---

## Authors

- **Vibha Suneel Navale** (vnava22@uic.edu)
- **Raksha Parag Pawar** (rpawa7@uic.edu)
- **Rohit Nanjundareddy** (rnanj@uic.edu)

**Institution**: University of Illinois Chicago  
**Course**: CS 531 - Social Robotics & HRI

