from datetime import date, datetime, time, timedelta

import streamlit as st

from src.storage import load_data, upsert_record
from src.validation import coerce_text

st.set_page_config(page_title="Daily Entry", page_icon="📝", layout="wide")



def to_time_string(value: time) -> str:
    return value.strftime("%H:%M")



def main() -> None:
    st.title("📝 Daily Entry")
    st.caption("Enter or update a daily record.")

    today = date.today()

    with st.form("daily_entry_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Dates and Dinner")
            record_date = st.date_input("Record date", value=today)
            dinner_date = st.date_input("Dinner date", value=record_date - timedelta(days=1))
            dinner_text = st.text_area(
                "What was dinner last night?",
                placeholder="Example: grilled chicken, rice, salad",
                height=120,
            )
            dinner_time = st.time_input("Dinner time", value=time(19, 0))
            overnight_urination_count = st.number_input(
                "Number of times you urinated overnight",
                min_value=0,
                max_value=20,
                value=0,
                step=1,
            )

        with col2:
            st.subheader("Today's Health Measurements")
            bp_systolic = st.number_input(
                "Blood pressure systolic (top number)", min_value=50, max_value=260, value=120, step=1
            )
            bp_diastolic = st.number_input(
                "Blood pressure diastolic (bottom number)", min_value=30, max_value=160, value=80, step=1
            )
            bp_time = st.time_input("Blood pressure time", value=time(8, 0))
            weight = st.number_input(
                "Weight", min_value=0.0, max_value=1000.0, value=180.0, step=0.1, format="%.1f"
            )
            weight_time = st.time_input("Weight time", value=time(7, 0))

        submitted = st.form_submit_button("Save record", use_container_width=True)

    if submitted:
        record = {
            "record_date": record_date.isoformat(),
            "dinner_date": dinner_date.isoformat(),
            "dinner_text": coerce_text(dinner_text),
            "dinner_time": to_time_string(dinner_time),
            "overnight_urination_count": int(overnight_urination_count),
            "bp_systolic": int(bp_systolic),
            "bp_diastolic": int(bp_diastolic),
            "bp_time": to_time_string(bp_time),
            "weight": float(weight),
            "weight_time": to_time_string(weight_time),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        upsert_record(record)
        st.success(f"Record for {record_date.isoformat()} saved to the local SQLite database.")

    st.divider()
    st.subheader("Existing Records")
    df = load_data()
    if df.empty:
        st.info("No records saved yet.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
