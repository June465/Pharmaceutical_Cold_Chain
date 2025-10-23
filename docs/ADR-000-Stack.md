# ADR-000: Core Technology Stack

## Status

Accepted

## Context

We need to select the core technologies for the blockchain node, the IoT simulator, the web explorer, and the orchestration layer. The goal is to choose a stack that is well-supported, relatively easy for beginners, and suitable for the project's requirements.

## Decision

We have decided on the following stack:

-   **Blockchain Node (`/node`):** Python 3 with the Flask framework.
    -   *Rationale:* Python is excellent for rapid prototyping. Flask is a lightweight and simple web framework, perfect for building the node's REST API. Its extensive libraries for cryptography and networking will be valuable in later phases.

-   **IoT Simulator (`/simulator`):** Python 3.
    -   *Rationale:* Using Python keeps the backend stack consistent. It's the de-facto language for data simulation and scripting, making it a natural choice for the simulator.

-   **Web Explorer (`/explorer`):** React (using Create React App).
    -   *Rationale:* React is the industry standard for building modern, interactive user interfaces. It has a massive ecosystem and community support.

-   **Orchestration (`/docker`):** Docker and Docker Compose.
    -   *Rationale:* This is the goal of Phase 0. It allows us to define and run our multi-container application with a single command, ensuring a consistent development environment for everyone.

## Consequences

-   Developers will need Python, Node.js, and Docker installed on their local machines.
-   The initial setup is focused on development and will need to be adapted for a production environment later (e.g., using a production-grade web server for Flask instead of the development server).