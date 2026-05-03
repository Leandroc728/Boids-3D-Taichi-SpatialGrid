# Boids 3D Ecosystem Simulation

![Taichi](https://img.shields.io/badge/Taichi-High_Performance-blue)
![Python](https://img.shields.io/badge/Python-3.12-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

> A real-time artificial life and emergent behavior simulation, rendering 50,000 simultaneous particles via massive GPU acceleration.

<div align="center">
  <img src="demonstrations/50000_boids/video.gif" alt="Boids 3D Demonstration with 50,000 Boids" width="600">
</div>

## About the Project

This project implements the **Boids** algorithm (developed by Craig Reynolds in 1986) in a 3D environment. Instead of calculating interactions on the CPU, the simulation was built using the **Taichi** programming language/library, which allows compiling Python code directly into high-performance GPU kernels (CUDA/Vulkan). Advanced data structuring techniques were also implemented to maximize processing efficiency.

## Architecture & Optimization

To overcome the classic O(N²) complexity bottleneck and execute parallel processing effectively, the project relies on two essential optimization techniques:

*   **Uniform Spatial Grid:** The 3D space is divided into a grid of small cells, drastically reducing the search space for each Boid. Consequently, each boid only searches for and interacts with neighbors located within its own cell or immediately adjacent ones.
*   **Data-Oriented Programming (DOP):** The code structure was designed specifically for how GPUs consume data. Utilizing Taichi's **fields**, boid data (such as position, velocity, and color) is aligned sequentially in memory. This organization ensures the GPU accesses information with maximum throughput and minimal latency.

## Features

Beyond implementing classic flocking rules, the simulation introduces advanced survival instincts and physics:

*   **Classic Rules (Flocking):**
    *   *Cohesion:* Boids steer to move toward the average position of local flockmates.
    *   *Alignment:* Boids steer towards the average heading of local flockmates.
    *   *Separation:* Boids steer to avoid crowding local flockmates.
*   **Survival Instincts:**
    *   *Predators (Hunting/Fleeing):* Red boids hunt the nearest target. Blue boids utilize a vision multiplier to detect and flee from danger.
    *   *Foraging:* Boids are attracted to green food sources scattered throughout the environment.
*   **Physics & Environment:** 
    *   Invisible boundary system (*Steer away from edges*).
    *   Gravity acceleration and speed gains during dives (*Dive Boost*).

## How to Run

### Prerequisites
Ensure you have Python 3.9+ installed and a dedicated GPU.

### Installation
```bash
# Clone the repository
git clone [https://github.com/Leandroc728/Boids-3D-Taichi-SpatialGrid.git](https://github.com/Leandroc728/Boids-3D-Taichi-SpatialGrid.git)

# Enter the directory
cd Boids-3D-Taichi-SpatialGrid

# Install dependencies
pip install -r requirements.txt
```

## User Interface

The project includes an interactive control panel for real-time parameter adjustment:

* Weight Sliders: Modify the intensity of cohesion, separation, fear, and other variables.

* Perception Radius: Adjust how far each boid can "see."

* Camera Controls: Use the Right Mouse Button to rotate and the W, A, S, D keys to navigate through the 3D space.

## Tools & References

* Python 3.12: Base language.
* Taichi Lang: JIT compilation for GPU.
