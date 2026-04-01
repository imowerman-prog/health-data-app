from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_FILE = DATA_DIR / "health_log.db"
LEGACY_CSV_FILE = DATA_DIR / "health_log.csv"

COLUMNS = [
    "record_date",
    "dinner_date",
    "dinner_text",
    "dinner_time",
    "overnight_urination_count",
    "bp_systolic",
    "bp_diastolic",
    "bp_time",
    "weight",
    "weight_time",
    "updated_at",
]


def _get_connection() -> sqlite3.Connection:
    ensure_database()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS health_log (
                record_date TEXT PRIMARY KEY,
                dinner_date TEXT,
                dinner_text TEXT,
                dinner_time TEXT,
                overnight_urination_count INTEGER,
                bp_systolic INTEGER,
                bp_diastolic INTEGER,
                bp_time TEXT,
                weight REAL,
                weight_time TEXT,
                updated_at TEXT
            )
            """
        )
        conn.commit()
    _migrate_legacy_csv_if_needed()



def _migrate_legacy_csv_if_needed() -> None:
    if not LEGACY_CSV_FILE.exists():
        return

    with sqlite3.connect(DB_FILE) as conn:
        existing_count = conn.execute("SELECT COUNT(*) FROM health_log").fetchone()[0]
        if existing_count > 0:
            return

    try:
        legacy_df = pd.read_csv(LEGACY_CSV_FILE)
    except Exception:
        return

    if legacy_df.empty:
        return

    legacy_df = legacy_df[[col for col in COLUMNS if col in legacy_df.columns]].copy()
    for col in COLUMNS:
        if col not in legacy_df.columns:
            legacy_df[col] = None
    legacy_df = legacy_df[COLUMNS]

    with sqlite3.connect(DB_FILE) as conn:
        legacy_df.to_sql("health_log", conn, if_exists="append", index=False)
        conn.commit()



def load_data() -> pd.DataFrame:
    with _get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT record_date, dinner_date, dinner_text, dinner_time, overnight_urination_count, "
            "bp_systolic, bp_diastolic, bp_time, weight, weight_time, updated_at "
            "FROM health_log ORDER BY record_date",
            conn,
        )

    if df.empty:
        return pd.DataFrame(columns=COLUMNS)

    numeric_cols = ["overnight_urination_count", "bp_systolic", "bp_diastolic", "weight"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["record_date"] = pd.to_datetime(df["record_date"], errors="coerce").dt.date.astype(str)
    df["dinner_date"] = pd.to_datetime(df["dinner_date"], errors="coerce").dt.date.astype(str)
    return df



def upsert_record(record: Dict[str, Any]) -> None:
    values = [record.get(col) for col in COLUMNS]
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO health_log (
                record_date, dinner_date, dinner_text, dinner_time, overnight_urination_count,
                bp_systolic, bp_diastolic, bp_time, weight, weight_time, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(record_date) DO UPDATE SET
                dinner_date=excluded.dinner_date,
                dinner_text=excluded.dinner_text,
                dinner_time=excluded.dinner_time,
                overnight_urination_count=excluded.overnight_urination_count,
                bp_systolic=excluded.bp_systolic,
                bp_diastolic=excluded.bp_diastolic,
                bp_time=excluded.bp_time,
                weight=excluded.weight,
                weight_time=excluded.weight_time,
                updated_at=excluded.updated_at
            """,
            values,
        )
        conn.commit()



def export_csv_bytes() -> bytes:
    df = load_data()
    return df.to_csv(index=False).encode("utf-8")
