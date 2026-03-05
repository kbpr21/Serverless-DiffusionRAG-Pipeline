# Serverless DiffusionRAG Pipeline

A cloud-native, cost-optimized **Retrieval-Augmented Generation (RAG)** application built with a diffusion-based LLM, vectorless retrieval, Infrastructure as Code, and fully automated CI/CD.

## Architecture

| Component | Technology |
|---|---|
| Backend | Python 3.10+ / FastAPI / Uvicorn |
| Retrieval | VectifyAI PageIndex (vectorless, reasoning-based) |
| LLM | Mercury 2 dLLM API (Inception Labs) |
| Containerization | Docker |
| Registry | Azure Container Registry (ACR) |
| Compute | Azure Container Apps (ACA) — scales to zero |
| IaC | Terraform |
| CI/CD | GitHub Actions |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/kbpr21/Serverless-DiffusionRAG-Pipeline.git
cd Serverless-DiffusionRAG-Pipeline

# 2. Create environment
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# 3. Set secrets
cp .env.example .env
# Fill in your actual keys in .env

# 4. Run locally
uvicorn app.main:app --reload
```

## Project Structure

```
├── app/                    # FastAPI application code
├── terraform/              # Terraform IaC configs
├── .github/workflows/      # CI/CD pipeline
├── docs/                   # PRD, tech-stack, to-do
├── tests/                  # Unit / integration tests
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Documentation

- [Product Requirements Document](docs/prd.md)
- [Tech Stack](docs/tech-stack.md)
- [To-Do / Roadmap](docs/to-do.md)

## License

This project is for educational and portfolio purposes.
