# JurisAI

**Multi-Agent Constraint-Aware Legal Reasoning & Case Analysis System**

JurisAI is an intelligent legal research and case analysis platform designed for Indian Family Law. It analyzes natural-language factual narratives using multiple specialized AI agents, Central Indian statutes, Supreme Court of India precedents, evidence evaluations, procedural constraints, and adversarial arguments to generate a structured, verifiable legal assessment.

---

## 1. System Requirements

Ensure the target machine has the following installed:

- **Python**: Version 3.10, 3.11, or 3.12
- **Node.js**: Version 18.x, 20.x, or 22.x
- **npm**: Version 9.x or higher
- **Git** (optional, for version management)

Supported Operating Systems: macOS, Linux (Ubuntu/Debian/Fedora), and Windows (PowerShell or WSL).

---

## 2. Quick Start: Setting Up on Another Device

You can run JurisAI on any new machine either via Docker Compose (all 5 services packaged together) or locally via Python and Node.js.

### Method A: One-Command Docker Deployment (Recommended)

Prerequisites: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

1. Navigate to the project root directory:
   ```bash
   cd /path/to/jurisai
   ```

2. Copy the example environment configuration:
   ```bash
   cp .env.example .env
   ```

3. Launch the complete containerized stack:
   ```bash
   docker compose up --build
   ```

The complete application will start with full persistence:
- **JurisAI Web App**: `http://localhost:5173`
- **FastAPI Backend & Swagger**: `http://localhost:8000/docs`
- **Prometheus Scraper**: `http://localhost:9090`
- **Grafana Observability Dashboard**: `http://localhost:3000/d/jurisai-observability-dashboard`
- **Ollama Inference Server**: `http://localhost:11434`

---

### Method B: Manual Local Setup (Python + Node.js)

### Step 1: Backend Setup (Python)

1. Open your terminal and navigate to the project root directory:
   ```bash
   cd /path/to/jurisai
   ```

2. Create a clean Python virtual environment:
   - On macOS / Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - On Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

3. Upgrade pip and install all backend dependencies from `requirements.txt`:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Verify that the pre-indexed ChromaDB vector store exists in `chroma_db/`. (All 916 legal chunks are already indexed and stored offline).

5. Start the FastAPI backend server:
   ```bash
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

   The backend will start and display:
   ```text
   INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   ```

   You can verify backend health by visiting:
   [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

### Step 2: Frontend Setup (React + Vite)

1. Open a **second terminal window** and navigate to the `frontend` folder:
   ```bash
   cd /path/to/jurisai/frontend
   ```

2. Install all frontend packages:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

   The frontend will start on port 5173:
   ```text
   VITE ready in 200 ms
   Local: http://localhost:5173/
   ```

4. Open your browser and navigate to:
   **[http://localhost:5173/](http://localhost:5173/)**

The Vite frontend automatically proxies all `/api` calls directly to `http://127.0.0.1:8000`, so both services work seamlessly together without cross-origin configuration.

---

## 3. Alternative: Single-Port Unified Production Mode

If you prefer to run both the frontend and backend on a single port (`8000`) without opening two terminal windows:

1. Build the production frontend bundle:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

2. Activate your virtual environment and start the backend:
   ```bash
   source .venv/bin/activate
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
   ```

3. Open **[http://localhost:8000/](http://localhost:8000/)** in your browser. The FastAPI server will serve both the compiled React application and the API endpoints directly from port 8000.

---

## 4. Project Architecture & Directory Layout

```text
jurisai/
├── backend/
│   ├── main.py                  # FastAPI server entry point and static mounting
│   ├── routes/
│   │   └── analysis.py          # API endpoints (/api/analyze, /api/upload-document, /api/health)
│   ├── models/
│   │   └── schemas.py           # Pydantic request and response schemas
│   └── services/
│       └── jurisai_engine.py    # Bridge between FastAPI and multi-agent reasoning loop
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LegalNavbar.jsx          # Top navigation with clean JurisAI mark
│   │   │   ├── LandingHero.jsx          # Scrollable homepage with 5 dimensions
│   │   │   ├── CaseInputSection.jsx     # Case description intake and document upload
│   │   │   ├── AgentProgressModal.jsx   # Live 8-stage execution tracker
│   │   │   ├── WorkspaceSidebar.jsx     # Left navigation sidebar (8 sections + chat)
│   │   │   ├── WorkspaceMainContent.jsx # Main analysis display (clean numbered format)
│   │   │   ├── HumanReadableLegalCard.jsx # Plain language + legal citation cards
│   │   │   ├── CaseChat.jsx             # Interactive follow-up consultation chat
│   │   │   └── PdfReportTemplate.jsx    # Court-ready PDF export (html2pdf.js)
│   │   ├── App.jsx              # Main orchestrator (Landing -> Workspace transition)
│   │   └── index.css            # Universal Calibri design system and courtroom theme
│   ├── vite.config.js           # Vite server configuration with /api reverse proxy
│   └── package.json             # Frontend dependencies (React, html2pdf.js, lucide-react)
├── chroma_db/                   # Persistent vector store (916 chunks indexed with FastEmbed)
├── chunks/                      # Extracted statutory and precedent chunk files
├── multi_agent_workflow.py      # Core 8-agent reasoning pipeline
├── reanalysis_system.py         # Self-checking Auditor and recovery loop
├── vector_query_service.py      # ChromaDB retrieval and embedding service
├── requirements.txt             # Python backend dependencies
└── README.md                    # System documentation and startup guide
```

---

## 5. Multi-Agent Pipeline Overview

JurisAI processes cases through eight specialized agents in a constraint-aware loop:

1. **Case Manager Agent**: Parses unstructured narrative text into normalized entities (parties, timeline, material facts, and claims).
2. **Law Agent**: Retrieves governing sections, requirements, and provisos from 12 Central Indian Acts.
3. **Precedent Agent**: Extracts binding ratio decidendi and official SCR/INSC citations from 91 Supreme Court judgments.
4. **Evidence Agent**: Audits factual assertions against proof standards, identifying supporting proof and evidence gaps.
5. **Constraint Hunter Agent**: Uncovers procedural bars, mandatory waiting periods (e.g. Section 13B(2) cooling-off), and withdrawal rights.
6. **Opposition Agent**: Acts as adversarial counsel to formulate defense objections and anticipate counterclaims.
7. **Auditor Agent**: Verifies every citation against India Code and Supreme Court records; triggers an automated self-repair loop if anomalies are detected.
8. **Judge Agent**: Synthesizes the final 11-section assessment with decree outlook and actionable next steps.

---

## 6. Supported Legal Scope

The system includes coverage across Central Indian family law statutes:

- Hindu Marriage Act, 1955
- Special Marriage Act, 1954
- Family Courts Act, 1984
- Protection of Women from Domestic Violence Act, 2005
- Guardian and Wards Act, 1890
- Hindu Minority and Guardianship Act, 1956
- Hindu Adoptions and Maintenance Act, 1956
- Code of Criminal Procedure, 1973 (Section 125) / Bharatiya Nagarik Suraksha Sanhita, 2023
- Indian Christian Marriage Act, 1872
- Divorce Act, 1869
- Parsi Marriage and Divorce Act, 1936
- Dissolution of Muslim Marriages Act, 1939

Precedent coverage includes 91 verified Supreme Court judgments from 2023 to 2025.

---

## 7. Observability, Logging & Monitoring (Phase 17)

JurisAI incorporates production-grade observability with structured application logging and Prometheus metrics exposed via `/metrics`.

### Architecture
```text
JurisAI Backend
   ↓ (Structured JSON Logs to logs/jurisai_app.log + Prometheus Counters/Histograms)
Prometheus (Scrapes http://127.0.0.1:8000/metrics every 5s)
   ↓
Grafana (Visualizes latency, agent durations, and case outcomes)
```

### Metrics Tracked:
- **API Request Count & Response Latency**: `jurisai_api_requests_total`, `jurisai_api_request_duration_seconds`
- **Case Analyses Outcomes**: `jurisai_case_analyses_total` (labeled by outcome and case_type)
- **Agent Execution Duration & Errors**: `jurisai_agent_execution_duration_seconds`, `jurisai_agent_failures_total`
- **RAG ChromaDB Search Latency & Chunk Counts**: `jurisai_rag_retrieval_duration_seconds`, `jurisai_rag_retrieved_documents_count`, `jurisai_rag_retrieval_failures_total`
- **Auditor Results & Self-Correction**: `jurisai_audit_results_total`, `jurisai_reanalysis_iterations_total`, `jurisai_reanalysis_loops_per_case`
- **Local LLM / Ollama Failures**: `jurisai_llm_failures_total`

### Structured Logging Format:
Every application log record in `logs/jurisai_app.log` adheres to the strict Phase 17 schema:
```json
{
  "timestamp": "2026-10-06T21:45:17.365769+00:00",
  "analysis_id": "trace-verified-007",
  "agent_name": "CaseManagerAgent",
  "status": "SUCCESS",
  "level": "INFO",
  "logger": "jurisai.orchestrator",
  "message": "CaseManagerAgent finished in 0.0007s",
  "duration": 0.0007,
  "case_type": "Child Custody, Guardianship & Visitation Dispute"
}
```

### Running Prometheus & Grafana
- **Prometheus config**: `monitoring/prometheus.yml`
- **Grafana config**: `monitoring/grafana/grafana.ini`
- **Grafana dashboard**: `monitoring/grafana/dashboards/jurisai-observability.json`

To launch Prometheus:
```bash
prometheus --config.file=monitoring/prometheus.yml --web.listen-address=127.0.0.1:9090
```

To launch Grafana:
```bash
grafana server --config monitoring/grafana/grafana.ini --homepath /opt/homebrew/opt/grafana/share/grafana
```

Grafana Access Credentials:
- URL: `http://localhost:3000` or `http://localhost:3000/d/jurisai-observability-dashboard`
- Username: `admin` OR `palak.wadhwani.23cse@bmu.edu.in`
- Password: `#Palak1702`
- Anonymous Viewer mode is also enabled for direct dashboard access.

---

## 8. Dockerization Architecture (Phase 18)

JurisAI features a production-ready, multi-container orchestration via Docker Compose with dedicated networks, persistent volumes, and healthchecks:
- **Backend Service (`jurisai-backend`)**: Containerized Python 3.11 with FastAPI, offline ChromaDB, PyMuPDF, and Prometheus instrumentation.
- **Frontend Service (`jurisai-frontend`)**: Multi-stage build (Node.js compile -> Nginx Alpine reverse proxy on port 80 / mapped to 5173).
- **Ollama Inference Engine (`jurisai-ollama`)**: Local high-performance model serving container.
- **Prometheus Scraper (`jurisai-prometheus`)**: Auto-discovers and scrapes `/metrics` across the bridge network.
- **Grafana Dashboard (`jurisai-grafana`)**: Auto-provisioned multi-agent telemetry dashboards with dark theme.

To deploy the complete 5-service container stack:
```bash
docker compose up --build -d
```

---

## 9. Testing & Evaluation Suite (Phase 19)

JurisAI incorporates a comprehensive, quantitative automated evaluation framework covering all 5 core dimensions:

```text
tests/
├── conftest.py                   # Session fixtures, vector store, test clients, and test matrices
├── test_rag_evaluation.py        # 1. RAG Evaluation (Hit Rate@K, MRR, Latency, Reranking boosts)
├── test_agent_evaluation.py      # 2. Agent Evaluation (8 individual agents & state transitions)
├── test_citation_accuracy.py     # 3. Citation Accuracy (Validation vs 12 Acts & 91 SC Judgments)
├── test_hallucination_testing.py # 4. Hallucination Testing (Adversarial fake sections & self-healing)
└── test_end_to_end.py            # 5. End-to-End Testing (FastAPI REST API & MultiAgent workflow)
```

### Running All Automated Tests:
```bash
source .venv/bin/activate
pytest tests/ -v
```

### Running the Master Evaluation Benchmark Scorecard:
```bash
python run_phase19_evaluation.py
```

### Latest Evaluation Scorecard (100% Passed):
- **Automated Tests**: 34 / 34 Passed (100.0%)
- **RAG Retrieval Hit Rate @ 3**: 100.0% (MRR: 1.0, Average Latency: 59.36ms)
- **Multi-Agent Pipeline**: 8 / 8 Agents Validated (100.0%)
- **Statutory Citation Precision**: 100.0% (0.0% Hallucinations across 12 Acts)
- **Precedent Citation Precision**: 100.0% (Verified official SCR/INSC Supreme Court citations)
- **Trivial/Greeting Input Rejection**: 100.0% (Gated with clean triage guidance)
- **Self-Repair Reanalysis Recovery**: 100.0% (Automated error detection -> re-routing -> recovery)
- **End-to-End REST API Status**: 100% HTTP 200 across `/api/health`, `/api/sample-cases`, `/api/analyze`, `/api/upload-document`, `/metrics`

---

## 10. Troubleshooting

### Port 8000 or Port 5173 is already in use
- To run the backend on a different port:
  ```bash
  python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
  ```
  If changing backend port, update the proxy target in `frontend/vite.config.js` to match.

### Document Upload (PDF extraction)
- PDF parsing utilizes PyMuPDF (`fitz`). If PyMuPDF encounters an issue on older Windows architectures, text files (`.txt`, `.md`, `.rtf`) are extracted directly in the browser with `FileReader` and can be analyzed immediately.

### Offline Vector Database
- The embeddings use FastEmbed (`BAAI/bge-small-en-v1.5`), which runs locally without requiring an OpenAI or external API key. The indexed database is contained in `chroma_db/`.

---

## 9. Disclaimer

JurisAI is an academic research and engineering platform. It provides structured legal reasoning and statutory analysis for educational, research, and self-help preparation purposes. It does not constitute formal legal counsel or substitute for an advocate enrolled under the Advocates Act, 1961.
