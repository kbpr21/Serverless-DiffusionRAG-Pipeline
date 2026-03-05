# Serverless DiffusionRAG Pipeline — Master To-Do

> Derived from [prd.md](file:///c:/Users/91630/Serverless-DiffusionRAG-Pipeline/docs/prd.md) and [tech-stack.md](file:///c:/Users/91630/Serverless-DiffusionRAG-Pipeline/docs/tech-stack.md).
> Each task is atomic and ordered so that every subsequent task builds on the previous one.

---

## Phase 0: Project Scaffolding & Prerequisites

- [ ] Create the root project directory structure:
  ```
  Serverless-DiffusionRAG-Pipeline/
  ├── app/              # FastAPI application code
  ├── terraform/        # IaC (Terraform) configs
  ├── .github/workflows # CI/CD pipeline definitions
  ├── docs/             # PRD, tech-stack, to-do (already exists)
  ├── tests/            # Unit / integration tests
  ├── Dockerfile
  ├── requirements.txt
  ├── .env.example      # Template for secrets (never commit .env)
  ├── .gitignore
  └── README.md
  ```
- [ ] Initialize `git` repo and push initial commit to GitHub
- [ ] Add a proper `.gitignore` (Python, Terraform state, `.env`, `__pycache__`, etc.)
- [ ] Create `.env.example` listing all required env vars:
  - `MERCURY_API_KEY`
  - `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` / `AZURE_TENANT_ID` / `AZURE_SUBSCRIPTION_ID`
- [ ] Verify you have an active **Azure Student Free Tier** subscription
- [ ] Install local prerequisites: `Python 3.10+`, `Docker Desktop`, `Terraform CLI`, `Azure CLI`

---

## Phase 1: The Local Backend Foundation

### 1.1 Python Environment
- [ ] Create a Python virtual environment (`python -m venv venv`)
- [ ] Create `requirements.txt` with pinned versions:
  - `fastapi`
  - `uvicorn[standard]`
  - `python-multipart` (file uploads)
  - `python-dotenv` (env management)
  - `httpx` (async HTTP for Mercury 2 API)
  - `pageindex` (VectifyAI — confirm exact package name / install method)
- [ ] Install dependencies and verify clean import

### 1.2 FastAPI Application (`app/main.py`)
- [ ] Create the entry-point `app/main.py` with the FastAPI app instance
- [ ] Implement **health-check** endpoint: `GET /health` → `{"status": "ok"}`
- [ ] Implement **document upload** endpoint: `POST /upload`
  - Accept `PDF` and `TXT` files via `UploadFile`
  - Save to an in-memory buffer (stateless — no disk persistence)
  - Parse document content and build a PageIndex tree structure
  - Return the generated tree/index metadata as confirmation
- [ ] Implement **query** endpoint: `POST /query`
  - Accept `{ "question": "...", "document_id": "..." }` (or similar schema)
  - Route the question + PageIndex context to **Mercury 2 API**
  - Return the generated answer as JSON
- [ ] Create Pydantic request/response schemas in `app/schemas.py`
- [ ] Create service module `app/services/retrieval.py` — PageIndex integration logic
- [ ] Create service module `app/services/llm.py` — Mercury 2 API call logic (async `httpx`)
- [ ] Store the Mercury 2 API key via `python-dotenv` → `.env` (never committed)

### 1.3 Local Testing & Validation
- [ ] Run the server locally: `uvicorn app.main:app --reload`
- [ ] Test `GET /health` via `curl` or browser
- [ ] Test `POST /upload` with a sample PDF and sample TXT
- [ ] Test `POST /query` end-to-end (upload → query → answer)
- [ ] Write basic unit tests under `tests/` (optional but recommended)

---

## Phase 2: Containerization

### 2.1 Dockerfile
- [ ] Write `Dockerfile` at project root:
  - Base image: `python:3.10-slim`
  - Copy `requirements.txt`, run `pip install --no-cache-dir`
  - Copy application code (`app/`)
  - Expose port `8000`
  - CMD: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Add `.dockerignore` (venv, `.git`, `terraform/`, `.env`, `__pycache__`, `docs/`)

### 2.2 Local Container Validation
- [ ] Build the image locally: `docker build -t diffusion-rag:local .`
- [ ] Run the container: `docker run -p 8000:8000 --env-file .env diffusion-rag:local`
- [ ] Re-run the same tests from Phase 1.3 against `localhost:8000` to confirm parity
- [ ] Verify the image size is reasonable (< 500 MB target)

---

## Phase 3: Cloud Infrastructure Setup (IaC with Terraform)

### 3.1 Azure Provider Configuration
- [ ] Create `terraform/providers.tf`:
  - `azurerm` provider with required features block
  - Backend config (local state file is fine for a student project)
- [ ] Create `terraform/variables.tf`:
  - `resource_group_name`, `location`, `acr_name`, `aca_env_name`, `aca_app_name`
  - Provide sensible defaults

### 3.2 Resource Definitions
- [ ] Create `terraform/main.tf`:
  - **Resource Group** (`azurerm_resource_group`)
  - **Azure Container Registry** (`azurerm_container_registry`) — Basic SKU (free-tier)
  - **ACA Environment** (`azurerm_container_app_environment`)
  - **ACA Container App** (`azurerm_container_app`)
    - Ingress: external, port `8000`
    - Scale: `min_replicas = 0`, `max_replicas = 1` ← critical for zero-cost idle
    - Image source: ACR (placeholder until CI/CD wires it)
    - Environment variables / secrets for `MERCURY_API_KEY`
- [ ] Create `terraform/outputs.tf`:
  - Output the ACA FQDN (public URL)
  - Output the ACR login server URL

### 3.3 Provision & Validate
- [ ] `az login` — authenticate with Azure Student account
- [ ] `cd terraform && terraform init`
- [ ] `terraform plan` — review the execution plan, ensure no unexpected costs
- [ ] `terraform apply -auto-approve` — provision infrastructure
- [ ] Verify resources in the Azure Portal:
  - Resource Group exists
  - ACR is accessible
  - ACA environment is created, container app shows 0 replicas (idle)

---

## Phase 4: CI/CD Automation (GitHub Actions)

### 4.1 Secrets Configuration
- [ ] In GitHub repo → **Settings → Secrets → Actions**, add:
  - `AZURE_CLIENT_ID`
  - `AZURE_CLIENT_SECRET`
  - `AZURE_TENANT_ID`
  - `AZURE_SUBSCRIPTION_ID`
  - `ACR_LOGIN_SERVER` (from Terraform output)
  - `ACR_USERNAME` / `ACR_PASSWORD` (ACR admin credentials)
  - `MERCURY_API_KEY`

### 4.2 Workflow File
- [ ] Create `.github/workflows/deploy.yml`:
  - **Trigger:** `push` to `main` branch only
  - **Job: build-and-deploy**
    1. Checkout code
    2. Login to Azure CLI (`azure/login@v2` action)
    3. Login to ACR (`docker login`)
    4. Build Docker image, tag with commit SHA + `latest`
    5. Push image to ACR
    6. Update the ACA revision to use the new image (via `az containerapp update`)
  - (Optional) Add a **test** job that runs before deploy

### 4.3 First Pipeline Run
- [ ] Push a commit to `main` and watch the Actions run
- [ ] Verify the workflow completes successfully (green check)
- [ ] Hit the ACA public FQDN → confirm `GET /health` returns `{"status": "ok"}`
- [ ] Test `POST /upload` and `POST /query` against the live URL

---

## Phase 5: Hardening & Documentation (Post-MVP Polish)

- [ ] Add **error handling** middleware in FastAPI (global exception handler)
- [ ] Add **request logging** (structured JSON logs for observability)
- [ ] Add **CORS middleware** if a frontend will be consuming the API
- [ ] Write a comprehensive `README.md`:
  - Project purpose & architecture diagram
  - Local development quickstart
  - Terraform provisioning instructions
  - CI/CD pipeline overview
  - API endpoint reference
- [ ] Add a basic **architecture diagram** to `docs/` (Mermaid or image)
- [ ] Validate the ACA scales to zero after ~5 min of inactivity (cost verification)
- [ ] Review Azure billing dashboard to confirm zero charges during idle

---

## Quick Reference — Key Commands

| Action | Command |
|---|---|
| Start local server | `uvicorn app.main:app --reload` |
| Build Docker image | `docker build -t diffusion-rag:local .` |
| Run Docker locally | `docker run -p 8000:8000 --env-file .env diffusion-rag:local` |
| Terraform init | `cd terraform && terraform init` |
| Terraform plan | `terraform plan` |
| Terraform apply | `terraform apply -auto-approve` |
| Terraform destroy | `terraform destroy -auto-approve` |
| Azure login | `az login` |
