import streamlit as st

from src.charts import bp_chart, overnight_chart, weight_chart
from src.storage import load_data

st.set_page_config(page_title="Trends", page_icon="📈", layout="wide")


def main() -> None:
    st.title("📈 Trends")
    st.caption("Monitor changes over time.")

    df = load_data()
    if df.empty:
        st.info("No records available yet. Add entries on the Daily Entry page.")
        return

    st.subheader("Overnight Urination")
    st.plotly_chart(overnight_chart(df), use_container_width=True)

    st.subheader("Blood Pressure")
    st.plotly_chart(bp_chart(df), use_container_width=True)

    st.subheader("Weight")
    st.plotly_chart(weight_chart(df), use_container_width=True)


if __name__ == "__main__":
    main()
