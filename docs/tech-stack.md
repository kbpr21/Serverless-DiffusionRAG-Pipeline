# Serverless DiffusionRAG - Tech Stack

This document outlines the core technologies used to build, deploy, and run the Serverless DiffusionRAG pipeline. The stack was strategically selected to optimize for ultra-low latency AI inference, completely vectorless retrieval, and zero-cost idle cloud computing.

## 🏗️ Infrastructure as Code (IaC)
* **Terraform:** The foundational provisioning engine.
  * *Strategic Advantage:* Used to declaratively define and provision the Azure Resource Group, Azure Container Registry (ACR), and the Azure Container Apps (ACA) environment, ensuring the entire cloud infrastructure is reproducible, version-controlled, and deployed without manual portal interaction.

## ♾️ CI/CD & Automation
* **GitHub:** Source code management and version control.
* **GitHub Actions:** The CI/CD engine. Automates the pipeline to build the application image, authenticate securely with Azure, and deploy the latest revision upon every push to the `main` branch.

## 🐳 Containerization & Storage
* **Docker:** Standardizes the application environment. Packages the Python backend, AI routing dependencies, and system libraries into a unified, portable container image.
* **Azure Container Registry (ACR):** A private cloud registry utilized as the secure storage layer for built Docker images prior to deployment.

## ☁️ Cloud Compute (Serverless)
* **Azure Container Apps (ACA):** The serverless execution environment hosting the Docker container. 
  * *Strategic Advantage:* Configured to scale down to zero replicas during idle periods, strictly adhering to Azure Student Free Tier constraints while offering instant spin-up for incoming API requests.

## ⚙️ Backend & Application Layer
* **Python 3.10+:** The primary programming language for backend logic and AI orchestration.
* **FastAPI:** A modern, high-performance web framework for building APIs with Python.
  * *Strategic Advantage:* Chosen for its asynchronous capabilities and native support for Pydantic data validation, making it the perfect lightweight host for handling external AI API requests.
* **Uvicorn:** An ASGI web server implementation for Python, running the FastAPI application inside the Docker container.

## 🧠 AI & Retrieval Engine
* **VectifyAI PageIndex:** The core retrieval framework. 
  * *Strategic Advantage:* Replaces traditional, cost-heavy vector databases by generating an agentic, reasoning-based tree structure (table of contents) from ingested documents for logical data routing.
* **Inception Labs Mercury 2 (via API):** The generative AI reasoning engine.
  * *Strategic Advantage:* A bleeding-edge diffusion-based LLM (dLLM). Utilized for its unparalleled generation speed (1,000+ tokens/second) and complex reasoning capabilities required to navigate the PageIndex tree structure without maintaining local hardware overhead.