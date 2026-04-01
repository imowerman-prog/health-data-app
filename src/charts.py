import pandas as pd
import plotly.graph_objects as go


def _chart_df(df: pd.DataFrame) -> pd.DataFrame:
    chart_df = df.copy()
    chart_df["record_date"] = pd.to_datetime(chart_df["record_date"], errors="coerce")
    return chart_df.sort_values("record_date")


def overnight_chart(df: pd.DataFrame) -> go.Figure:
    chart_df = _chart_df(df)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_df["record_date"],
            y=chart_df["overnight_urination_count"],
            mode="lines+markers",
            name="Overnight urinations",
        )
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Count",
        hovermode="x unified",
    )
    return fig


def bp_chart(df: pd.DataFrame) -> go.Figure:
    chart_df = _chart_df(df)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_df["record_date"],
            y=chart_df["bp_systolic"],
            mode="lines+markers",
            name="Systolic",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["record_date"],
            y=chart_df["bp_diastolic"],
            mode="lines+markers",
            name="Diastolic",
        )
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Blood pressure",
        hovermode="x unified",
    )
    return fig


def weight_chart(df: pd.DataFrame) -> go.Figure:
    chart_df = _chart_df(df)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_df["record_date"],
            y=chart_df["weight"],
            mode="lines+markers",
            name="Weight",
        )
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Weight",
        hovermode="x unified",
    )
    return fig
