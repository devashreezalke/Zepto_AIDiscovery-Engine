# Zepto Category Discovery Engine: Deployment Plan

This document outlines the step-by-step deployment procedure to host the Python ETL/API backend on **Railway** and the interactive Next.js dashboard frontend on **Vercel** under $0/month free-tier plans.

---

## 🏗️ Deployment Topology

```
                   ┌──────────────────────────────────────┐
                   │          Vercel Frontend             │
                   │    (Next.js React Dashboard)         │
                   └──────────────────┬───────────────────┘
                                      │
                                      │ HTTPS JSON Feed Fetch
                                      ▼
                   ┌──────────────────────────────────────┐
                   │          Railway Backend             │
                   │    (FastAPI API + Python ETL)        │
                   └──────────────────┬───────────────────┘
                                      │
                                      │ Local Persistent Read/Write
                                      ▼
                   ┌──────────────────────────────────────┐
                   │       SQLite Database Volume         │
                   │         (/data/discovery.db)         │
                   └──────────────────────────────────────┘
```

---

## 🚀 Part A: Railway Backend & Ingestion Pipeline

Railway is used to run the background scraping and analysis pipeline and serve the insights JSON feed dynamically via FastAPI.

### 1. Project Configuration Files
The project root contains the following key configuration files:
*   [app.py](file:///c:/Users/GIRISH/OneDrive/Documents/Zepto_discovery/Zepto_AIDiscovery-Engine/app.py): The FastAPI web server that serves `/api/insights` and exposes a `/api/run-pipeline` POST webhook.
*   [requirements.txt](file:///c:/Users/GIRISH/OneDrive/Documents/Zepto_discovery/Zepto_AIDiscovery-Engine/requirements.txt): Lists all Python dependencies (`fastapi`, `uvicorn`, `pptx`, `docx`, `scikit-learn`, `numpy`, `groq`).

### 2. Deploy Steps on Railway
1.  **Create a Railway Account:** Sign up at [Railway.app](https://railway.app/).
2.  **Install Railway CLI (Optional):**
    ```bash
    npm install -g @railway/cli
    railway login
    ```
3.  **Link GitHub Repository:**
    *   Click **"New Project"** in the Railway dashboard.
    *   Select **"Deploy from GitHub repo"** and choose your linked repository.
4.  **Add a Persistent Disk Volume (Crucial for SQLite):**
    *   SQLite is a file-based database. Since Railway's filesystem is ephemeral (resets on deploy), you **must** mount a volume to persist data.
    *   Click **"Add Source"** -> **"Volume"**.
    *   Mount the Volume at path: `/data`.
5.  **Configure Environment Variables:**
    In the Railway service settings under **"Variables"**, add:
    *   `PORT` = `8000` (FastAPI listens to this port).
    *   `GROQ_API_KEY` = `your_actual_groq_api_key` (Unlocks live AI synthesis).
    *   `DATABASE_URL` = `/data/discovery.db` (Points SQLite to the mounted persistent volume).
6.  **Railway Deploy Command:**
    Railway automatically detects Python applications and starts them using `uvicorn app:app` via Nixpacks. If you need to override it, add the Start command in service settings:
    ```bash
    python -m uvicorn app:app --host 0.0.0.0 --port $PORT
    ```

### 3. Setup Recurring Cron Pipeline
To run the ingestion and validation scripts daily:
1.  Add a **Railway Cron Job** under your project panel.
2.  Set the schedule to run daily (e.g., `0 2 * * *` - everyday at 2:00 AM).
3.  Set the execution command to:
    ```bash
    python run_pipeline.py
    ```

---

## 🎨 Part B: Vercel Frontend Dashboard

Vercel is used to host the Next.js React user interface.

### 1. Update Frontend Configuration
The Next.js dashboard at `/dashboard` has been updated to dynamically fetch from the absolute Railway API url when deployed, falling back to local static cache files during offline runs.

### 2. Deploy Steps on Vercel
1.  **Create Vercel Account:** Sign up at [Vercel.com](https://vercel.com/) (linked to your GitHub account).
2.  **Import New Project:**
    *   Click **"Add New"** -> **"Project"** in the Vercel dashboard.
    *   Import your GitHub repository.
3.  **Configure Root Directory:**
    *   In the setup panel, click **"Edit"** next to **Root Directory** and select `dashboard`. (Vercel will build only the Next.js code rather than the root Python codebase).
4.  **Set Environment Variables:**
    *   Add key: `NEXT_PUBLIC_API_URL`.
    *   Set the value to your Railway live deployment URL (e.g. `https://zepto-discovery-production.up.railway.app`).
5.  **Deploy:**
    *   Click **"Deploy"**. Vercel will build the React code and serve it at a custom `.vercel.app` domain.

---

## 🔒 Security & Data Integrity

1.  **PII Sanitization:** The ingestion scraper automatically strips email addresses and phone numbers before writing to SQLite, ensuring no customer PII is stored on Railway or exposed on Vercel.
2.  **Database Backups:** You can download the persistent `discovery.db` file at any time from your Railway volume panel or by running:
    ```bash
    railway volume download <volume-id> ./data/backup_discovery.db
    ```
