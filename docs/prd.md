# Product Requirements Document (PRD)

**Project Name:** Serverless DiffusionRAG Pipeline

**Status:** In Development

**Objective:** To design, build, and automate a cloud-native, cost-optimized Retrieval-Augmented Generation (RAG) application utilizing a diffusion-based LLM, vectorless retrieval, Infrastructure as Code (IaC), and a fully automated CI/CD pipeline.

---

### 1. Project Overview

This project demonstrates advanced DevOps, SRE, LLMOps, and cloud architecture capabilities. It shifts away from traditional, expensive vector databases and standard autoregressive LLMs by integrating a reasoning-based tree index (PageIndex) with a high-speed diffusion model (Mercury 2). The entire infrastructure is provisioned via code using Terraform, automated via GitOps principles, and deployed onto serverless cloud compute to strictly maintain zero operational costs during idle periods.

### 2. The Tech Stack & Architecture

| Component | Technology | Purpose in Pipeline |
| --- | --- | --- |
| **Infrastructure as Code** | Terraform | Declaratively provisions the Azure Resource Group, ACR, and ACA to ensure reproducible environments. |
| **Source Control & CI/CD** | GitHub & GitHub Actions | Triggers automated builds and deployments upon code push. |
| **Containerization** | Docker | Packages the Python environment and dependencies for consistent cloud execution. |
| **Container Registry** | Azure Container Registry (ACR) | Securely stores the built Docker images in the cloud. |
| **Compute Engine** | Azure Container Apps (ACA) | Serverless host for the API; scales to zero to protect student tier credits. |
| **Backend Framework** | Python (FastAPI) | Handles web requests, routing, and orchestrates the AI logic. |
| **Retrieval Engine** | VectifyAI PageIndex | Generates reasoning-based, vectorless tree structures from documents. |
| **LLM Inference** | Mercury 2 API (Inception Labs) | Provides ultra-low latency, diffusion-based text generation and reasoning. |

---

### 3. Functional Requirements

* The system must expose a REST API endpoint via FastAPI to receive user queries.
* The backend must accept document uploads (PDF/TXT) and process them using the PageIndex framework.
* The system must route the structured data and user query to the Mercury 2 API for reasoning and generation.
* The CI/CD pipeline must automatically build a new Docker image whenever code is merged into the `main` branch.
* The CI/CD pipeline must automatically deploy the latest image to Azure Container Apps without manual intervention.

### 4. Non-Functional Requirements

* **Cost Constraints:** The infrastructure must remain strictly within the Azure Student Free Tier limits. The compute service must scale to zero when idle.
* **Statelessness:** The Azure Container App must be entirely stateless; any required data processing happens in-memory or via external API calls during the request lifecycle.
* **Latency:** By utilizing the Mercury 2 dLLM API, inference response times should aim to stay significantly lower than standard autoregressive open-source models.

---

### 5. Execution Plan (Phase-by-Phase)

**Phase 1: The Local Backend Foundation**

* Initialize the Python environment and install FastAPI, Uvicorn, and PageIndex.
* Write the `main.py` script to define the API endpoints.
* Integrate the Mercury 2 API key and test the reasoning logic locally.

**Phase 2: Containerization**

* Write the `Dockerfile` to package the FastAPI application.
* Build and run the Docker container locally to ensure environmental parity.

**Phase 3: Cloud Infrastructure Setup (IaC)**

* Write the `main.tf` configuration file to define the Azure Resource Group, Azure Container Registry (ACR), and Azure Container Apps (ACA) environment.
* Explicitly configure ACA scale rules via Terraform (Min replicas: 0, Max replicas: 1) for cost optimization.
* Run `terraform init`, `plan`, and `apply` to provision the infrastructure automatically.

**Phase 4: CI/CD Automation**

* Create the `.github/workflows/deploy.yml` file.
* Configure Azure authentication secrets in the GitHub repository.
* Run the first automated pipeline to push the code from GitHub to the live Azure infrastructure managed by Terraform.

---