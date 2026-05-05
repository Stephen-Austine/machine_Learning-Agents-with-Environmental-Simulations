# 🤖 Machine Learning Agents — Environmental Simulations

A collection of intelligent agent simulations demonstrating core AI agent architectures from foundational AI theory. Each agent operates within a two-location vacuum-cleaner environment and showcases progressively more sophisticated decision-making capabilities — from simple reflex behaviour to full utility-maximisation and adaptive performance tuning.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Agent Architectures](#agent-architectures)
  - [1. Model-Based Reflex Agent](#1-model-based-reflex-agent)
  - [2. Goal-Oriented Vacuum Agent](#2-goal-oriented-vacuum-agent)
  - [3. Adaptive Performance Learning Agent](#3-adaptive-performance-learning-agent)
  - [4. Utility-Based Agent](#4-utility-based-agent)
- [Environment Design](#environment-design)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Simulations](#running-the-simulations)
- [Concepts Illustrated](#concepts-illustrated)
- [Sample Output](#sample-output)
- [Future Improvements](#future-improvements)

---

## Overview

This project implements and simulates four distinct AI agent types rooted in the PEAS framework (Performance, Environment, Actuators, Sensors) from classical AI literature. The vacuum-cleaner world — a well-known benchmark environment in AI education — serves as the shared test bed. Each simulation builds on the previous one, adding layers of intelligence:

| Agent | Intelligence Level | Key Feature |
|---|---|---|
| Model-Based Reflex | Reactive + Memory | Tracks past cleaning methods |
| Goal-Oriented | Reactive + Goal | Runs until environment is clean (24-cycle loop) |
| Adaptive Performance | Learning | Monitors its own score and adjusts behaviour mid-run |
| Utility-Based | Deliberative | Maximises a multi-component utility function on a grid world |

---

## Project Structure

```
machine_Learning Agents. Evironmental Simulations/
│
├── Model-Based-Reflex-Vacuum-Agent.py          # Single-run model-based reflex agent
├── Goal-Oriented-Vacuum-Agent-Simulation.ipynb # 24-cycle goal-driven agent (Jupyter)
├── Adaptive-Performance-Learning-Agent.ipynb   # Self-monitoring adaptive agent (Jupyter)
└── utility_Based_agent.py                      # Full utility-based grid-world agent
```

---

## Agent Architectures

### 1. Model-Based Reflex Agent

**File:** `Model-Based-Reflex-Vacuum-Agent.py`

A reactive agent that extends simple reflex behaviour by maintaining an internal model of the world — specifically, a history of which cleaning method (`T` or `L`) was last used at each location.

**How it works:**
- The `environment` class initialises two locations (`A` and `B`) with randomly assigned dirt conditions (`0` = clean, `1` = dirty) and a random starting position for the vacuum.
- A `cleaningmethod` dictionary stores the last cleaning mode used at each location, simulating internal state/memory.
- The `agent` class traverses both locations once per run. If a location is dirty, it cleans it and **toggles** the recorded cleaning method (`T` → `L` or `L` → `T`), adapting its approach based on prior history.
- After processing both locations, the agent prints the updated conditions and cleaning history.

**Key design pattern:**
```python
# Toggle cleaning method based on past behaviour
if environment.cleaningmethod[location] == "T":
    environment.cleaningmethod[location] = "L"
else:
    environment.cleaningmethod[location] = "T"
```

**Agent type in AIMA taxonomy:** *Model-based reflex agent* — it perceives the environment, maintains internal state, and acts according to condition-action rules.

---

### 2. Goal-Oriented Vacuum Agent

**File:** `Goal-Oriented-Vacuum-Agent-Simulation.ipynb`

Extends the model-based reflex agent with a **persistent goal**: keep both locations clean over time by running for 24 consecutive cycles (simulating 24 hours of operation, with a 1-second delay between cycles to simulate hourly checks).

**How it works:**
- The same `environment` and `agent` logic from the Model-Based Reflex Agent is reused.
- A `while x < 24` loop re-instantiates the environment and agent on each iteration, modelling the real-world scenario where dirt reappears randomly over time.
- `time.sleep(1)` between iterations simulates the passage of time (each iteration represents one hour).
- The agent's **goal** is simply to ensure both locations are clean at the end of every cycle — it always succeeds because it visits every location per run.

**Simulation loop:**
```python
x = 0
while x < 24:
    e1 = environment()
    a1 = agent(e1)
    x += 1
    time.sleep(1)  # Simulates 1-hour interval
```

**Agent type:** *Simple goal-based agent* — acts to achieve a defined goal (all rooms clean) repeatedly over time.

---

### 3. Adaptive Performance Learning Agent

**File:** `Adaptive-Performance-Learning-Agent.ipynb`

The most advanced of the vacuum agents. This agent **monitors its own performance score** mid-run and **dynamically adjusts its operating schedule** — demonstrating a basic form of self-directed learning and adaptation.

**How it works:**
- A `performance` class tracks a cumulative `score` (incremented by 1 each time a dirty location is cleaned) and calculates performance as a percentage out of a maximum possible score of 48 (`score / 48 * 100`).
- The agent runs for 24 cycles. At the **midpoint (cycle 12)**, performance is evaluated:
  - If performance **> 50%**: the agent resets `x = 0` and keeps `timeinterval = 1` second, increasing the frequency of visits (it's doing well and continues at pace).
  - If performance **≤ 50%**: `timeinterval` is increased to 3 seconds and `x` jumps forward by 3, reducing the total number of remaining visits (conserving resources when the environment is mostly clean).
- The `agent` class uses multiple inheritance from both `environment` and `performance`, demonstrating Python's MRO in action.

**Adaptation logic:**
```python
if x == 12:  # Mid-run checkpoint
    p = thescore.display()
    if p > 50:
        x = 0
        timeinterval = 1
        print("Increasing visits and intervals")
    else:
        timeinterval = 3
        x += 3
        print("Reducing visits and intervals")
```

**Agent type:** *Learning agent with performance element* — measures its own effectiveness and adjusts its strategy accordingly.

---

### 4. Utility-Based Agent

**File:** `utility_Based_agent.py`

A fully deliberative agent operating on a **10×10 grid world**. Rather than following fixed rules, this agent **evaluates every available action** by computing a weighted utility score and selects the action that maximises expected value. It also updates its utility weights after each action based on the reward received.

#### Core Classes

**`Action` (Enum)**
Eight possible actions: `MOVE_UP`, `MOVE_DOWN`, `MOVE_LEFT`, `MOVE_RIGHT`, `PICKUP`, `DROP`, `USE`, `WAIT`.

**`WorldState` (Dataclass)**
A snapshot of the world at a given time step, capturing:
- `agent_position` — current (x, y) coordinate
- `items_at_position` — items available to pick up
- `agent_inventory` — items currently held
- `world_map` — the full grid
- `time`, `energy`, `score`

**`UtilityBasedAgent`**

The agent computes a composite utility score before each action using five weighted components:

| Component | Weight | Description |
|---|---|---|
| Energy | 1.0 | Normalised remaining energy (`energy / 100`) |
| Score | 2.0 | Logarithmic score utility (`log(1 + score) / 10`) |
| Inventory Value | 1.5 | Total value of held items (gold=10, treasure=15, food=5, etc.) |
| Item Proximity | 0.8 | Inverse Manhattan distance to the nearest valuable item |
| Safety | 1.2 | Distance from grid edges (stay away from boundaries) |

```python
total_utility = (
    weights['energy']           * energy_utility    +
    weights['score']            * score_utility     +
    weights['inventory_value']  * inventory_utility +
    weights['item_proximity']   * proximity_utility +
    weights['safety']           * safety_utility
)
```

**Exploration vs. Exploitation:**  
An **ε-greedy strategy** (ε = 0.1) introduces 10% random action selection, preventing the agent from getting stuck in local optima.

**Online Weight Updates:**  
After each action, utility weights are scaled proportionally to the reward signal — positive rewards increase all weights, while negative rewards reduce them (with a floor of 0.1 to prevent weight collapse).

**`Environment`**

A 10×10 grid populated with:
- Gold (`g`) at positions (2,3) and (7,8) — reward: 20
- Food (`f`) at positions (1,1), (5,5), (8,2) — reward: 10
- Treasure (`t`) at position (9,9) — reward: 50

Items are removed from the grid upon pickup. Movement costs a penalty of −1 per step.

---

## Environment Design

All vacuum-based agents (Agents 1–3) share a common two-location stochastic environment:

```
Locations:     A, B
Dirt status:   0 (clean) or 1 (dirty)  — randomly initialised each cycle
Vacuum start:  Random (A or B)
Cleaning mode: T or L  — randomly initialised, toggled after each clean
```

The utility-based agent (Agent 4) uses a richer grid-world environment:

```
Grid size:     10 × 10
Cell types:    . (empty), g (gold), f (food), t (treasure)
Agent energy:  100 units (decays by 0.2 per step)
Episodes:      3 (default), 50 steps each
```

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Jupyter Notebook or JupyterLab (for `.ipynb` files)
- The following Python packages:

```
numpy
```

> All other dependencies (`random`, `math`, `time`, `typing`, `dataclasses`, `enum`) are part of the Python standard library.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/ml-agents-environmental-simulations.git
   cd ml-agents-environmental-simulations
   ```

2. **Install dependencies:**
   ```bash
   pip install numpy
   ```

3. **Launch Jupyter (for notebook files):**
   ```bash
   jupyter notebook
   ```

### Running the Simulations

**Model-Based Reflex Agent (single run):**
```bash
python "Model-Based-Reflex-Vacuum-Agent.py"
```

**Utility-Based Agent (full simulation):**
```bash
python utility_Based_agent.py
```

**Notebook simulations:**

Open each `.ipynb` file in Jupyter and run all cells:
- `Goal-Oriented-Vacuum-Agent-Simulation.ipynb` — runs 24 cycles with 1-second intervals
- `Adaptive-Performance-Learning-Agent.ipynb` — runs 24 cycles with mid-run performance evaluation

> ⚠️ The notebook simulations use `time.sleep()` delays, so they run in real time. The goal-oriented simulation takes approximately 24 seconds to complete; the adaptive agent may take up to 72 seconds depending on the performance branch taken.

---

## Concepts Illustrated

| Concept | Where Demonstrated |
|---|---|
| Stochastic environment | All agents — random dirt initialisation each cycle |
| Internal state / model | Model-Based Reflex Agent — `cleaningmethod` dictionary |
| Goal-based behaviour | Goal-Oriented Agent — operates until 24-cycle goal is met |
| Performance measurement | Adaptive Agent — `score / 48 * 100` performance metric |
| Self-adaptation | Adaptive Agent — adjusts visit frequency at midpoint |
| Utility functions | Utility-Based Agent — multi-component weighted utility |
| State prediction | Utility-Based Agent — `predict_next_state()` lookahead |
| ε-greedy exploration | Utility-Based Agent — 10% random action selection |
| Online learning | Utility-Based Agent — reward-proportional weight updates |
| Multi-inheritance (Python) | Adaptive Agent — `agent(environment, performance)` |

---

## Sample Output

**Model-Based Reflex Agent:**
```
Environment condition {'A': 1, 'B': 0} Vacuum location B cleaning method {'A': 'T', 'B': 'L'}
B Is clean
A  is dirty,
A Has been cleaned
new conditions {'A': 0, 'B': 0}
updated history {'A': 'L', 'B': 'L'}
```

**Adaptive Performance Agent (mid-run checkpoint):**
```
Score:  13
Performance:  27.083333333333332 %
Reducing visits and intervals
```

**Utility-Based Agent:**
```
=== Episode 1 ===
Step 0: Pos=(0, 0), Energy=100.0, Score=0, Inventory=[]
Step 20: Pos=(3, 4), Energy=96.0, Score=20, Inventory=['gold']
Step 40: Pos=(6, 7), Energy=92.0, Score=30, Inventory=['gold', 'food']
Episode 1 completed:
  Final Score: 30
  Total Reward: 9.00
  Final Inventory: ['gold', 'food']
  Utility Weights: {'energy': 1.04, 'score': 2.08, ...}
```

---

## Future Improvements

- **Expand the vacuum environment** to more than two locations (n-room grid)
- **Visualise the grid world** using `matplotlib` or `pygame` for the utility-based agent
- **Implement Q-learning or Deep RL** to replace hand-crafted utility weights with learned value functions
- **Add a comparison dashboard** plotting score and energy across all agent types on the same environment seeds
- **Introduce adversarial dirt** — dirt reappears probabilistically mid-episode to test robustness
- **Persist agent weights** across episodes using file I/O or a database

---

## References

- Russell, S. & Norvig, P. — *Artificial Intelligence: A Modern Approach* (4th ed.) — Chapter 2: Intelligent Agents
- Wooldridge, M. — *An Introduction to MultiAgent Systems* — Agent architectures overview
- Sutton, R. & Barto, A. — *Reinforcement Learning: An Introduction* — ε-greedy exploration, reward signals

---

*Built with Python 3.12 · Jupyter Notebook · numpy*
