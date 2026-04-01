import pandas as pd
import streamlit as st

from src.github_backup import backup_now, backup_status_lines, get_backup_config
from src.storage import DB_FILE, ensure_database, export_csv_bytes, load_data

st.set_page_config(
    page_title="Health Monitor",
    page_icon="🩺",
    layout="wide",
)

ensure_database()


def metric_value(df: pd.DataFrame, column: str) -> str:
    if df.empty:
        return "—"
    value = df.iloc[-1][column]
    if pd.isna(value) or value == "":
        return "—"
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)



def main() -> None:
    st.title("🩺 Night & Blood Pressure Health Monitor")
    st.caption("Track overnight urination, dinner, blood pressure, and weight in one place.")

    with st.sidebar:
        st.header("Navigation")
        st.write("Use the pages in the sidebar:")
        st.write("- **Daily Entry** for new or updated records")
        st.write("- **Trends** for charts and monitoring")
        st.divider()
        for line in backup_status_lines():
            st.write(line)

    df = load_data()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Records", len(df))
    col2.metric("Latest Overnight Urinations", metric_value(df, "overnight_urination_count"))
    col3.metric("Latest BP", f"{metric_value(df, 'bp_systolic')}/{metric_value(df, 'bp_diastolic')}")
    col4.metric("Latest Weight", metric_value(df, "weight"))

    st.subheader("Overview")
    st.write(
        "This app stores one record per **record date** in a local SQLite database. "
        "A new submission for the same date updates that day's values."
    )

    if df.empty:
        st.info("No records yet. Open **Daily Entry** from the sidebar to add your first entry.")
    else:
        st.subheader("Recent Entries")
        preview_cols = [
            "record_date",
            "dinner_text",
            "overnight_urination_count",
            "bp_systolic",
            "bp_diastolic",
            "weight",
        ]
        st.dataframe(df[preview_cols].tail(10), use_container_width=True, hide_index=True)

        st.download_button(
            label="Download data as CSV",
            data=export_csv_bytes(),
            file_name="health_log_export.csv",
            mime="text/csv",
        )

    st.subheader("Backup to GitHub")
    st.write(
        "Use the button below to push a backup copy of your local SQLite database and a CSV export to GitHub. "
        "A **private backup repository** is strongly recommended."
    )

    config = get_backup_config()
    if config is None:
        st.warning(
            "GitHub backup is not configured yet. Follow the README instructions to add your repo owner, repo name, branch, "
            "and GitHub token to `.env` locally and to Streamlit secrets for the deployed app."
        )
    else:
        st.success(
            f"Ready to back up to `{config.owner}/{config.repo}` on branch `{config.branch}`."
        )

    if st.button("Back Up to GitHub", use_container_width=True):
        try:
            message = backup_now()
            st.success(message)
        except Exception as exc:
            st.error(f"Backup failed: {exc}")

    st.subheader("Storage Note")
    st.info(
        "SQLite is reliable on your own computer because it writes to a real database file. "
        "On Streamlit Community Cloud, local files are still not guaranteed to survive every restart or redeploy, "
        "so the GitHub backup button is an added safety measure rather than a perfect database replacement."
    )


if __name__ == "__main__":
    main()
