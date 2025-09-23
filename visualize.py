import os
import pandas as pd
import plotly.graph_objects as go
import numpy as np


def visualize(title):

    journeys = pd.read_csv(
        os.path.join("in", title, "journeys.csv"), skipinitialspace=True
    )
    cost_threshold = pd.read_csv(os.path.join("out", title, "cost_threshold.csv"))
    pt_journeys = pd.read_csv(os.path.join("out", title, "pt_journeys.csv"))
    odm_journeys = pd.read_csv(os.path.join("out", title, "odm_journeys.csv"))
    blacklist_violations = pd.read_csv(
        os.path.join("out", title, "blacklist_violations.csv")
    )
    whitelist_violations = pd.read_csv(
        os.path.join("out", title, "whitelist_violations.csv")
    )

    journeys["departure"] = pd.to_datetime(
        journeys["departure"], utc=True
    ).dt.tz_convert("Europe/Berlin")
    journeys["arrival"] = pd.to_datetime(journeys["arrival"], utc=True).dt.tz_convert(
        "Europe/Berlin"
    )
    cost_threshold["time"] = pd.to_datetime(
        cost_threshold["time"], utc=True
    ).dt.tz_convert("Europe/Berlin")
    pt_journeys["departure"] = pd.to_datetime(
        pt_journeys["departure"], utc=True
    ).dt.tz_convert("Europe/Berlin")
    pt_journeys["center"] = pd.to_datetime(
        pt_journeys["center"], utc=True
    ).dt.tz_convert("Europe/Berlin")
    pt_journeys["arrival"] = pd.to_datetime(
        pt_journeys["arrival"], utc=True
    ).dt.tz_convert("Europe/Berlin")
    odm_journeys["departure"] = pd.to_datetime(
        odm_journeys["departure"], utc=True
    ).dt.tz_convert("Europe/Berlin")
    odm_journeys["center"] = pd.to_datetime(
        odm_journeys["center"], utc=True
    ).dt.tz_convert("Europe/Berlin")
    odm_journeys["arrival"] = pd.to_datetime(
        odm_journeys["arrival"], utc=True
    ).dt.tz_convert("Europe/Berlin")
    blacklist_violations["time"] = pd.to_datetime(
        blacklist_violations["time"], utc=True
    ).dt.tz_convert("Europe/Berlin")
    whitelist_violations["time"] = pd.to_datetime(
        whitelist_violations["time"], utc=True
    ).dt.tz_convert("Europe/Berlin")

    journeys["first_mile_duration"] = journeys["first_mile_duration"].apply(
        lambda x: pd.Timedelta(x, unit="m")
    )
    journeys["last_mile_duration"] = journeys["last_mile_duration"].apply(
        lambda x: pd.Timedelta(x, unit="m")
    )
    odm_journeys["travel_time"] = odm_journeys["travel_time"].apply(
        lambda x: pd.Timedelta(x, unit="m")
    )
    odm_journeys["odm_time"] = odm_journeys["odm_time"].apply(
        lambda x: pd.Timedelta(x, unit="m")
    )

    fig = go.Figure()

    # threshold
    fig.add_trace(
        go.Scatter(
            x=cost_threshold["time"],
            y=cost_threshold["cost"],
            name="Cost Threshold",
            line=dict(color="gray"),
        )
    )

    # violations
    fig.add_trace(
        go.Scatter(
            x=blacklist_violations["time"],
            y=blacklist_violations["cost"],
            name="Blacklist Violation",
            mode="markers",
            marker=dict(
                color="black",
                symbol="square",
                size=12,
                line=dict(width=2, color="red"),
            ),
            hoverinfo="none",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=whitelist_violations["time"],
            y=whitelist_violations["cost"],
            name="Whitelist Violation",
            mode="markers",
            marker=dict(
                color="white",
                symbol="square",
                size=12,
                line=dict(width=2, color="red"),
            ),
            hoverinfo="none",
        )
    )

    # pt
    fig.add_trace(
        go.Scatter(
            x=pt_journeys["center"],
            y=pt_journeys["cost"],
            name="PT",
            mode="markers",
            marker=dict(color="blue"),
            customdata=np.stack(
                (
                    pt_journeys["departure"],
                    pt_journeys["arrival"],
                    pt_journeys["travel_time"],
                    pt_journeys["transfers"],
                    pt_journeys["cost"],
                ),
                axis=-1,
            ),
            hovertemplate="<b>Departure</b>: %{customdata[0]}<br>"
            + "<b>Arrival</b>: %{customdata[1]}<br>"
            + "<b>Travel time</b>: %{customdata[2]}<br>"
            + "<b>Transfers</b>: %{customdata[3]}<br>"
            + "<b>Cost</b>: %{customdata[4]}",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=pt_journeys["departure"],
            y=pt_journeys["cost"],
            mode="markers",
            marker=dict(color="blue", symbol=142),
            hoverinfo="none",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=pt_journeys["arrival"],
            y=pt_journeys["cost"],
            mode="markers",
            marker=dict(color="blue", symbol=142),
            hoverinfo="none",
            showlegend=False,
        )
    )
    for j in pt_journeys.itertuples():
        fig.add_shape(
            type="line",
            x0=j.departure,
            y0=j.cost,
            x1=j.arrival,
            y1=j.cost,
            line=dict(width=1, color="blue"),
        )

    # odm
    for j in odm_journeys.itertuples():
        journeys_row = journeys[
            (journeys["departure"] == j.departure)
            & (journeys["arrival"] == j.arrival)
            & (journeys["transfers"] == j.transfers)
            & (
                (journeys["first_mile_mode"] == "taxi")
                | (journeys["last_mile_mode"] == "taxi")
            )
            & (
                journeys["first_mile_duration"] + journeys["last_mile_duration"]
                == j.odm_time
            )
        ].reset_index()
        first_mile_end = j.departure + (
            journeys_row.at[0, "first_mile_duration"]
            if journeys_row.at[0, "first_mile_mode"] == "taxi"
            else pd.Timedelta(0, unit="m")
        )
        last_mile_begin = j.arrival - (
            journeys_row.at[0, "last_mile_duration"]
            if journeys_row.at[0, "last_mile_mode"] == "taxi"
            else pd.Timedelta(0, unit="m")
        )

        fig.add_shape(
            type="line",
            x0=j.departure,
            y0=j.cost,
            x1=first_mile_end,
            y1=j.cost,
            line=dict(width=1, color="orange"),
            layer="below",
        )
        fig.add_shape(
            type="line",
            x0=first_mile_end,
            y0=j.cost,
            x1=last_mile_begin,
            y1=j.cost,
            line=dict(width=1, color="blue"),
            layer="below",
        )
        fig.add_shape(
            type="line",
            x0=last_mile_begin,
            y0=j.cost,
            x1=j.arrival,
            y1=j.cost,
            line=dict(width=1, color="orange"),
            layer="below",
        )
    fig.add_trace(
        go.Scatter(
            x=odm_journeys["center"],
            y=odm_journeys["cost"],
            name="ODM",
            mode="markers",
            marker=dict(color="orange"),
            customdata=np.stack(
                (
                    odm_journeys["departure"],
                    odm_journeys["arrival"],
                    odm_journeys["travel_time"],
                    odm_journeys["transfers"],
                    odm_journeys["odm_time"],
                    odm_journeys["cost"],
                ),
                axis=-1,
            ),
            hovertemplate="<b>Departure</b>: %{customdata[0]}<br>"
            + "<b>Arrival</b>: %{customdata[1]}<br>"
            + "<b>Travel time</b>: %{customdata[2]}<br>"
            + "<b>Transfers</b>: %{customdata[3]}<br>"
            + "<b>ODM Time</b>: %{customdata[4]}<br>"
            + "<b>Cost</b>: %{customdata[5]}",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=odm_journeys["departure"],
            y=odm_journeys["cost"],
            mode="markers",
            marker=dict(color="orange", symbol=142),
            hoverinfo="none",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=odm_journeys["arrival"],
            y=odm_journeys["cost"],
            mode="markers",
            marker=dict(color="orange", symbol=142),
            hoverinfo="none",
            showlegend=False,
        )
    )

    fig.update_layout(
        title=dict(
            text=title,
            xanchor="left",
            y=0.85,
            font=dict(size=13),
        ),
        legend=dict(
            x=1,
            y=1.15,
            xanchor="right",
            orientation="h",
        ),
    )

    fig.show()
