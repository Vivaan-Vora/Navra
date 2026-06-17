# Grid-Nexus

## Why Verdex Exists

Verdex was founded on a clear and painful observation: warehouse automation teams often spend more money recovering from navigation failures than they spend on the robots themselves.

Existing approaches like hardcoded route maps and shallow obstacle avoidance logic fail under normal warehouse volatility. A moved pallet, a temporary aisle blockage, or a crossing forklift can force repeated human intervention.

Verdex is building a simulation-first navigation intelligence layer that operators can apply to current robot fleets without replacing hardware.

Grid-Nexus is the technical rebrand of this project and unifies simulation, training, diagnostics, and benchmark tooling.

## Verdex

Grid-Nexus is a Python project for 2D warehouse robot navigation simulation with pathfinding and reinforcement learning.

## The Problem

Fixed paths break in changing warehouses.

## The Solution

Train adaptive policies in simulation and evaluate with rich metrics.

## What Was Built

Core environment generation, sensors, pathfinding, and project structure were implemented with supporting modules.

## Tools And Libraries

Python, NumPy, PyTorch, and Matplotlib.

## Repository Structure

```text
grid-nexus/
├── main.py
├── environment.py
├── sensors.py
├── pathfinder.py
├── q_agent.py
├── dqn_agent.py
├── visualizer.py
├── logger.py
├── benchmark.py
├── diagnostics.py
├── scorer.py
├── analyzer.py
├── failure_logger.py
├── comparator.py
├── generate_examples.py
├── config.json
├── requirements.txt
└── README.md
```

<!-- Add screenshot here: easy environment -->

![Description](docs/images/easy_env.png)

<!-- Add screenshot here: medium environment -->

![Description](docs/images/medium_env.png)

<!-- Add screenshot here: hard environment -->

![Description](docs/images/hard_env.png)

<!-- Add screenshot here: sensor rays -->

![Description](docs/images/sensor_rays.png)

<!-- Add screenshot here: pathfinding -->

![Description](docs/images/pathfinding.png)

<!-- Add screenshot here: q metrics -->

![Description](docs/images/q_metrics.png)

<!-- Add screenshot here: dqn metrics -->

![Description](docs/images/dqn_metrics.png)

<!-- Add screenshot here: benchmark chart -->

![Description](docs/images/benchmark.png)

<!-- Add screenshot here: diagnostics -->

![Description](docs/images/diagnostics.png)

<!-- Add screenshot here: vns -->

![Description](docs/images/vns.png)

<!-- Add screenshot here: edi -->

![Description](docs/images/edi.png)

<!-- Add screenshot here: failure pie -->

![Description](docs/images/failure_pie.png)

<!-- Add screenshot here: failure heatmap -->

![Description](docs/images/failure_heatmap.png)

<!-- Add screenshot here: comparator frame -->

![Description](docs/images/comparator_frame.png)

<!-- Add screenshot here: product tiers -->

![Description](docs/images/product_tiers.png)
