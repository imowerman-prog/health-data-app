from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, RequestException
from urllib.request import Request, urlopen

import streamlit as st

from src.storage import BASE_DIR, DB_FILE, export_csv_bytes, load_data

DEFAULT_BACKUP_DB_PATH = "backups/health_log.db"
DEFAULT_BACKUP_CSV_PATH = "backups/health_log_export.csv"


@dataclass
class GitHubBackupConfig:
    owner: str
    repo: str
    token: str
    branch: str = "main"
    db_path: str = DEFAULT_BACKUP_DB_PATH
    csv_path: str = DEFAULT_BACKUP_CSV_PATH



def _get_secret(name: str) -> Optional[str]:
    if name in st.secrets:
        return st.secrets[name]
    return os.getenv(name)



def get_backup_config() -> Optional[GitHubBackupConfig]:
    owner = _get_secret("GITHUB_BACKUP_OWNER")
    repo = _get_secret("GITHUB_BACKUP_REPO")
    token = _get_secret("GITHUB_BACKUP_TOKEN")
    branch = _get_secret("GITHUB_BACKUP_BRANCH") or "main"
    db_path = _get_secret("GITHUB_BACKUP_DB_PATH") or DEFAULT_BACKUP_DB_PATH
    csv_path = _get_secret("GITHUB_BACKUP_CSV_PATH") or DEFAULT_BACKUP_CSV_PATH

    if not owner or not repo or not token:
        return None

    return GitHubBackupConfig(
        owner=owner,
        repo=repo,
        token=token,
        branch=branch,
        db_path=db_path,
        csv_path=csv_path,
    )



def _github_request(url: str, token: str, method: str = "GET", data: bytes | None = None) -> dict:
    req = Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "streamlit-health-monitor-app",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(req, timeout=30) as response:
        payload = response.read()
        return json.loads(payload.decode("utf-8")) if payload else {}



def _get_existing_sha(config: GitHubBackupConfig, path: str) -> Optional[str]:
    url = f"https://api.github.com/repos/{config.owner}/{config.repo}/contents/{path}?ref={config.branch}"
    try:
        response = _github_request(url, config.token)
        return response.get("sha")
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise



def _upload_file(config: GitHubBackupConfig, path: str, content: bytes, message: str) -> None:
    sha = _get_existing_sha(config, path)
    url = f"https://api.github.com/repos/{config.owner}/{config.repo}/contents/{path}"
    payload = {
        "message": message,
        "content": base64.b64encode(content).decode("utf-8"),
        "branch": config.branch,
    }
    if sha:
        payload["sha"] = sha
    _github_request(url, config.token, method="PUT", data=json.dumps(payload).encode("utf-8"))



def backup_now() -> str:
    config = get_backup_config()
    if config is None:
        raise RuntimeError(
            "GitHub backup is not configured. Add GITHUB_BACKUP_OWNER, GITHUB_BACKUP_REPO, and "
            "GITHUB_BACKUP_TOKEN to your local .env file or Streamlit secrets."
        )

    if not DB_FILE.exists():
        raise RuntimeError("The SQLite database file does not exist yet. Save at least one record first.")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_message = f"Backup SQLite database from Streamlit app at {timestamp}"
    csv_message = f"Backup CSV export from Streamlit app at {timestamp}"

    _upload_file(config, config.db_path, DB_FILE.read_bytes(), db_message)
    _upload_file(config, config.csv_path, export_csv_bytes(), csv_message)
    return f"Backed up database and CSV snapshot to {config.owner}/{config.repo} on branch {config.branch}."



def backup_status_lines() -> list[str]:
    config = get_backup_config()
    lines = [f"Local SQLite file: `{DB_FILE}`"]
    if config is None:
        lines.append("GitHub backup: not configured yet")
    else:
        lines.append(
            f"GitHub backup target: `{config.owner}/{config.repo}` on branch `{config.branch}`"
        )
        lines.append(f"Database backup path: `{config.db_path}`")
        lines.append(f"CSV backup path: `{config.csv_path}`")
    return lines
