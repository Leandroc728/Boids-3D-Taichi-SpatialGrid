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

## Architecture and Optimization

To overcome the O(N²) complexity bottleneck and leverage massive GPU processing, the project relies on two fundamental strategies:

### 1. Uniform Spatial Grid (USG)
The 3D space is subdivided into a grid of fixed-size cells. Instead of each Boid comparing its position with all other N elements in the simulation, it only queries its own cell and the 26 neighboring cells.
* **O(N) Guarantee:** To ensure performance even in high-density scenarios, I implemented a strict search limit per cell (`max_boids_per_cell`). This transforms the neighbor search into an O(1) constant time operation per boid, resulting in an overall O(N) linear complexity.

### 2. Data-Oriented Programming (DOP)
Unlike traditional Object-Oriented Programming, where data is scattered in memory, I used the **DOP** approach through Taichi fields (`ti.field`).
* **Memory Layout:** Position and velocity data are stored contiguously. This maximizes data locality and allows the GPU to perform much more efficient global memory accesses, drastically reducing processing latency.

---

### Technical Results
* **Complexity:** Reduced from O(N²) to O(N).
* **Scalability:** Ability to process **50,000 agents** simultaneously.
* **Efficiency:** Smooth execution (40+ FPS) even on entry-level/integrated hardware (Intel Iris Xe).

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
git clone https://github.com/Leandroc728/Boids-3D-Taichi-SpatialGrid.git

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
