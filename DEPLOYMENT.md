# JurisAI: Deployment Guide (Render & Vercel)

This guide provides step-by-step instructions to deploy JurisAI with the **FastAPI Backend on Render** and the **React (Vite) Frontend on Vercel**, ensuring all multi-agent legal reasoning, document extraction, user authentication, and search history work seamlessly.

---

## Architecture Overview

```
                      +-----------------------------+
                      |       Vercel (Frontend)     |
                      |   React 19 + Vite SPA       |
                      |   Domain: your-app.vercel.app
                      +--------------+--------------+
                                     |
                       HTTPS / CORS  | Bearer Auth Header
                                     v
                      +-----------------------------+
                      |       Render (Backend)      |
                      |   FastAPI + Uvicorn         |
                      |   Domain: your-app.onrender.com
                      +--------------+--------------+
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
        +-----------------------+         +-----------------------+
        |   SQLite Auth DB      |         |  ChromaDB Vector DB   |
        |  Users, Sessions,     |         |  916 Legal Chunks     |
        |  Analysis History     |         |  (FastEmbed BGE)      |
        +-----------------------+         +-----------------------+
```

---

## Part 1: Deploy the Backend on Render

You can deploy the backend using Render's native **Python Web Service** (or via Docker).

### Step 1.1: Create a Web Service
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** > **Web Service**.
3. Connect your Git repository (or public Git URL).
4. Configure the service settings:
   - **Name**: `jurisai-backend` (or your chosen name)
   - **Region**: Choose the closest region (e.g., `Oregon`, `Frankfurt`)
   - **Runtime**: `Python`
   - **Branch**: `main` (or your working branch)
   - **Root Directory**: `.` (leave default)
   - **Build Command**:
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt && python build_vector_db.py
     ```
   - **Start Command**:
     ```bash
     python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: `Free` or `Starter`

### Step 1.2: Set Environment Variables on Render
Under the **Environment** tab on Render, add the following variables:

| Key | Recommended Value | Notes |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.11.9` | Ensures compatible Python runtime |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | Path where vector store is indexed |
| `CORS_ORIGINS` | `*` (or your Vercel URL) | Allows cross-origin requests from Vercel |
| `HOST` | `0.0.0.0` | Default host binding |

*(Optional for persistence)*: On the free tier, SQLite files (`./data/jurisai_auth.db`) reset on redeploy. If you want permanent user persistence across redeploys, you can upgrade to a Starter plan and attach a **Persistent Disk** mounted at `/var/data`, then add `AUTH_DB_PATH=/var/data/jurisai_auth.db`.

### Step 1.3: Verify Backend Deployment
Once Render finishes deploying:
1. Open `https://<your-render-service>.onrender.com/api/health`.
2. You should receive a JSON response:
   ```json
   {
     "status": "healthy",
     "service": "JurisAI Legal Reasoning Backend",
     "acts_covered": 12,
     "precedents_indexed": 91,
     "chroma_master_chunks": 916
   }
   ```
3. Copy your Render service URL (e.g., `https://jurisai-backend.onrender.com`). You will need it in Part 2.

> **Tip (Render Blueprint)**: Alternatively, Render can read the included [render.yaml](./render.yaml) automatically if you deploy via **New + > Blueprint**.

---

## Part 2: Deploy the Frontend on Vercel

### Step 2.1: Import Project to Vercel
1. Log in to [Vercel Dashboard](https://vercel.com).
2. Click **Add New...** > **Project**.
3. Select and import your Git repository.

### Step 2.2: Configure Project Settings
Vercel will detect Vite. Configure the build parameters:

- **Framework Preset**: `Vite`
- **Root Directory**: `frontend` (or leave as `.` if using root `vercel.json`)
- **Build Command**: `npm run build`
- **Output Directory**: `dist` (if root directory is `frontend`) or `frontend/dist` (if root directory is `.`)

### Step 2.3: Add Environment Variable
Under **Environment Variables**, add:

| Key | Value | Example |
| :--- | :--- | :--- |
| `VITE_API_URL` | Your Render backend URL (no trailing slash) | `https://jurisai-backend.onrender.com` |

4. Click **Deploy**.

Vercel will build and assign you a live production URL (e.g. `https://jurisai-client.vercel.app`).

---

## Part 3: Verification & Testing Checklist

Once both services are deployed, test the full application flow:

1. **Authentication (Register & Login)**:
   - Click the **"Counsel Login / Register"** button in the navigation bar.
   - Create a new account with username, email, and password.
   - Verify that you are automatically logged in, the token is stored, and your profile displays.
2. **Case Analysis**:
   - Paste a legal dispute narrative into the intake area (or click **"Load DV & Maintenance Sample"**).
   - Click **"Analyze Case with Multi-Agent System"**.
   - Watch the 8-agent execution trace modal run and redirect to the multi-tab Case Analysis Workspace.
3. **Document Upload**:
   - In the intake section, upload a `.pdf` or `.txt` legal petition or FIR.
   - Verify that text is extracted and attached to the analysis.
4. **Search & Case History**:
   - Click **"History"** in the top navigation bar.
   - Verify that the past analysis appears chronologically.
   - Click **"Restore Full Case State"** to restore previous analyses.
5. **Observability**:
   - Visit `https://<your-render-url>/metrics` to view Prometheus metrics.

---

## Part 4: Committing Changes to Somebody Else's Git Repository

Because you are contributing these changes to an existing project or another developer's repository, follow these clean Git practices:

### Step 4.1: Create a Dedicated Feature Branch
Never commit directly to `main` when working on someone else's repository.
```bash
# Check status
git status

# Create and switch to a descriptive branch
git checkout -b feature/render-vercel-deployment
```

### Step 4.2: Inspect Modified & Added Files
Run `git status` to see what has changed:
```bash
git status
```

**Added deployment files**:
- `render.yaml` — Render Blueprint configuration for FastAPI backend
- `vercel.json` — Vercel root SPA routing and build configuration
- `frontend/vercel.json` — Vercel frontend folder routing configuration
- `frontend/src/api/config.js` — Centralized API client supporting `VITE_API_URL`
- `frontend/.env.example` — Example environment variable for frontend
- `DEPLOYMENT.md` — This deployment guide

**Updated project files (clean and non-breaking)**:
- `backend/main.py` — Dynamic CORS handling for cross-origin Vercel requests
- `backend/services/auth_service.py` — Added `AUTH_DB_PATH` environment variable support
- `vector_query_service.py` — Auto-recovery for vector database initialization and bounds-checking
- `Dockerfile` — Included chunks build step and dynamic `$PORT` binding for cloud container environments
- `.env.example` — Added `CORS_ORIGINS` and `VITE_API_URL` examples
- `.gitignore` — Allowed essential chunk files needed for remote indexing
- `frontend/src/components/*` — Replaced hardcoded localhost endpoints with dynamic API client

### Step 4.3: Stage and Commit
```bash
git add render.yaml vercel.json frontend/vercel.json frontend/.env.example
git add frontend/src/api/config.js
git add frontend/src/App.jsx frontend/src/components/AuthModal.jsx frontend/src/components/SearchHistoryModal.jsx
git add frontend/src/components/CaseInputSection.jsx frontend/src/components/DocumentUpload.jsx frontend/src/components/WorkspaceMainContent.jsx
git add backend/main.py backend/services/auth_service.py vector_query_service.py Dockerfile .env.example .gitignore
git add chunks/all_legal_chunks.json chunks/judgment_chunks.json chunks/statute_chunks.json
git add DEPLOYMENT.md

git commit -m "feat(deploy): add Render and Vercel deployment configs with cross-origin auth"
```

### Step 4.4: Push to Remote & Create Pull Request
```bash
git push -u origin feature/render-vercel-deployment
```
Then open a Pull Request with a clear summary:
> **Summary**: Adds zero-downtime deployment support for Render (backend) and Vercel (frontend), including CORS support for cross-domain requests, dynamic API routing, automated vector store initialization, and full user authentication & search history restoration across deployments.

---

## Part 5: Collaboration & Automatic Continuous Deployment (CI/CD)

### Can You Commit New Changes Once Added as a Collaborator?
**Yes, absolutely!** 

When the repository owner adds you as a **Collaborator** on GitHub:

1. **Direct Commit Permissions**: You gain push access to the repository. You can push commits directly or merge Pull Requests into the production branch (`main`).
2. **Automatic Redeployments on Render**:
   - Because `render.yaml` sets `autoDeploy: true`, any commit pushed or merged into `main` automatically triggers Render to build and deploy the new version without any manual button clicks.
3. **Automatic Redeployments on Vercel**:
   - Vercel automatically listens to GitHub webhooks. Every push to `main` instantly triggers a new production deployment.
   - For every Pull Request or feature branch, Vercel also automatically generates an isolated **Preview Deployment** (with its own unique URL) so you can test changes before merging to production.
4. **Instant Rollbacks**: If a newly pushed commit introduces an issue, both Render and Vercel keep a complete history of previous successful deployments, allowing you to roll back with a single click in their dashboards.

### If You Are NOT a Direct Collaborator Yet (Fork Workflow):
If the repository owner has not added you yet:
1. Fork the owner's repository to your personal GitHub account.
2. Link your personal fork to Render and Vercel (your personal deployments will auto-update on every commit you push).
3. Whenever you want to contribute updates to the original project, create a Pull Request from your fork back to their original repository.
4. Once the owner accepts your PR and/or adds you as a collaborator, future changes can be pushed directly.

