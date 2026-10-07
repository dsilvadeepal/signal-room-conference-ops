"""Plotly figures used by the Signal Room dashboard."""

import pandas as pd
import plotly.graph_objects as go

SURFACE = "#141B2D"
TEXT = "#F4F7FB"
MUTED = "#AAB6CF"
GRID = "#283554"
STATUS_COLORS = {"attention": "#FF6B7A", "monitor": "#F6C85F", "healthy": "#5DDBB4"}


def build_bubble_chart(snapshot: pd.DataFrame) -> go.Figure:
    eligible = snapshot[snapshot["plot_eligible"].astype(bool)]
    figure = go.Figure()
    for status in ("attention", "monitor", "healthy"):
        rows = eligible[eligible["status"].eq(status)]
        if rows.empty:
            continue
        figure.add_trace(go.Scatter(
            x=rows["attendee_pulse_score"], y=rows["operations_pressure_per_100"],
            customdata=rows[["entity_name"]].to_numpy(), mode="markers", name=status.title(),
            marker={"size": rows["people_affected"], "sizemode": "area", "sizeref": 0.12,
                    "color": STATUS_COLORS[status], "line": {"color": "#F4F7FB", "width": 1}},
            text=rows["entity_name"], hovertemplate="<b>%{text}</b><br>Pulse: %{x}<br>Operations pressure: %{y:.1f}<extra></extra>",
        ))
    figure.update_layout(
        title="Experience pulse vs. operations pressure", height=470,
        xaxis_title="Attendee pulse score (1–5)", yaxis_title="Support cases per 100 attendees",
        legend_title="Status", template="plotly_dark", paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font={"color": TEXT}, legend={"font": {"color": TEXT}},
        xaxis={"gridcolor": GRID, "zerolinecolor": GRID, "color": MUTED},
        yaxis={"gridcolor": GRID, "zerolinecolor": GRID, "color": MUTED},
    )
    return figure


def build_trend_chart(entity_history: pd.DataFrame) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=entity_history["timestamp"], y=entity_history["occupancy_rate"],
                                mode="lines+markers", name="Occupancy (%)", line={"color": "#6EA8FE"}))
    figure.add_trace(go.Scatter(x=entity_history["timestamp"], y=entity_history["avg_queue_minutes"],
                                mode="lines+markers", name="Queue (min)", yaxis="y2", line={"color": "#FF6B7A"}))
    figure.update_layout(
        title="Selected entity trend", template="plotly_dark", height=340, paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE, font={"color": TEXT},
        yaxis={"title": "Occupancy (%)", "gridcolor": GRID, "zerolinecolor": GRID, "color": MUTED},
        yaxis2={"title": "Queue (min)", "overlaying": "y", "side": "right", "gridcolor": GRID, "color": MUTED},
        legend={"orientation": "h", "font": {"color": TEXT}},
    )
    return figure
