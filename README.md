# Streamlit Health Monitor App

A professional starter Streamlit app for tracking:

- overnight urination count
- dinner from the previous night
- dinner time
- blood pressure (systolic and diastolic) and time taken
- weight and time taken

This version uses **SQLite locally** and includes a **Back Up to GitHub** button that can push both the SQLite database file and a CSV export to a GitHub repository.

## Project Structure

```text
streamlit_health_monitor_app/
├── app.py
├── pages/
│   ├── 1_Daily_Entry.py
│   └── 2_Trends.py
├── src/
│   ├── charts.py
│   ├── github_backup.py
│   ├── storage.py
│   └── validation.py
├── data/
│   ├── health_log.db
│   └── health_log.csv          # only used if migrating older CSV data
├── .streamlit/
│   └── secrets.toml.example
├── .env.example
├── requirements.txt
├── .gitignore
└── README.md
```

## Features

- multipage Streamlit app
- daily entry form
- one saved record per record date
- local SQLite persistence
- trend charts for overnight urination, blood pressure, and weight
- CSV export
- manual GitHub backup button
- backup configuration through `.env` or Streamlit secrets

## What Is More Reliable About This Version

### Local use in VS Code

When you run the app on your own computer, data are stored in:

```text
data/health_log.db
```

That SQLite file is much more reliable than a CSV as the main store.

### Deployed use on Streamlit Community Cloud

Even with SQLite, the deployed app is still writing to the local filesystem of the Streamlit environment, and Streamlit does **not** guarantee that local files survive every restart, rebuild, or redeploy.

So this version adds a **Back Up to GitHub** button.

That means your practical setup becomes:

- **working data store:** local SQLite file
- **backup copy:** GitHub repository
- **manual trigger:** button in the app

For personal health-style data, use a **private GitHub repo**, not a public one.

## What You Need To Create In GitHub

You should create **two repositories**:

### 1. App code repository
This is the repo that contains the Streamlit code and is connected to Streamlit Community Cloud.

Example:

```text
streamlit-health-monitor-app
```

### 2. Backup repository
This is where the app will upload the database backup and CSV snapshot when you press the backup button.

Example:

```text
streamlit-health-monitor-backups
```

Make this one **private**.

## What You Need To Modify

There are four values you must customize for backup:

- `GITHUB_BACKUP_OWNER`
- `GITHUB_BACKUP_REPO`
- `GITHUB_BACKUP_BRANCH`
- `GITHUB_BACKUP_TOKEN`

Optional values:

- `GITHUB_BACKUP_DB_PATH`
- `GITHUB_BACKUP_CSV_PATH`

### Example

```text
GITHUB_BACKUP_OWNER=your-github-name
GITHUB_BACKUP_REPO=streamlit-health-monitor-backups
GITHUB_BACKUP_BRANCH=main
GITHUB_BACKUP_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

## Local Setup in Visual Studio Code

### 1. Clone your app repo

```bash
git clone <your-app-repo-url>
cd streamlit-health-monitor-app
```

### 2. Create and activate a virtual environment

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install packages

```bash
pip install -r requirements.txt
```

### 4. Create your local backup config

Copy the example file:

```bash
cp .env.example .env
```

Then open `.env` and replace these placeholders:

- `your-github-username-or-org`
- `your-private-backup-repo-name`
- `your-github-fine-grained-or-classic-token`

You may leave the branch as `main` unless your backup repo uses a different default branch.

## How To Create The GitHub Token

Create a GitHub token that can write contents to the **backup repo**.

A fine-grained token is best. Give it access to:

- the backup repository only
- repository contents: read and write

Then place that token in:

```text
.env
```

as:

```text
GITHUB_BACKUP_TOKEN=your-token-here
```

## How To Run The App Locally

```bash
streamlit run app.py
```

## How The Backup Button Works

When you click **Back Up to GitHub**, the app uploads:

- `data/health_log.db` to the backup repo path in `GITHUB_BACKUP_DB_PATH`
- a CSV export to the backup repo path in `GITHUB_BACKUP_CSV_PATH`

By default those go to:

```text
backups/health_log.db
backups/health_log_export.csv
```

inside the backup repository.

## Deploying To Streamlit Community Cloud

### 1. Push the app code to GitHub

```bash
git add .
git commit -m "Initial SQLite health monitor app with GitHub backup"
git push origin main
```

### 2. Create the app in Streamlit Community Cloud

- sign in to Streamlit Community Cloud
- create a new app
- select your **app code repo**
- set the main file path to `app.py`
- deploy

### 3. Add your backup secrets in Streamlit

In the Streamlit app settings, open **Secrets** and add the values from `.streamlit/secrets.toml.example` with your real values.

For example:

```toml
GITHUB_BACKUP_OWNER = "your-github-name"
GITHUB_BACKUP_REPO = "streamlit-health-monitor-backups"
GITHUB_BACKUP_BRANCH = "main"
GITHUB_BACKUP_TOKEN = "your-real-token"
GITHUB_BACKUP_DB_PATH = "backups/health_log.db"
GITHUB_BACKUP_CSV_PATH = "backups/health_log_export.csv"
```

Then save the secrets and restart the app if needed.

## Recommended Workflow

### For your own computer

- enter records locally
- SQLite stores them in `data/health_log.db`
- click **Back Up to GitHub** periodically

### For the deployed Streamlit app

- enter records
- do **not** assume local SQLite on Streamlit is permanent
- click **Back Up to GitHub** after important entries

## Privacy Recommendation

Because this app contains personal health-style information, do **not** back up to a public repository.

Use:

- a **private backup repo**
- a GitHub token with the smallest necessary permissions

## Data Schema

Each record stores:

- `record_date`
- `dinner_date`
- `dinner_text`
- `dinner_time`
- `overnight_urination_count`
- `bp_systolic`
- `bp_diastolic`
- `bp_time`
- `weight`
- `weight_time`
- `updated_at`

## Suggested Next Enhancements

- notes about sleep quality
- alcohol / caffeine / sodium checkboxes
- medication tracking
- multi-user login with per-user separation
- automatic backup schedule outside the app
- migration to Postgres or Supabase for stronger cloud persistence
