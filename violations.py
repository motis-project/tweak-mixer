import os
import pandas as pd


def contains(dataframe, journey):
    return (
        len(
            dataframe[
                (dataframe["departure"] == journey.departure)
                & (dataframe["arrival"] == journey.arrival)
                & (dataframe["transfers"] == journey.transfers)
            ].index
        )
        > 0
    )


def violations(title):
    forbidden = pd.read_csv(
        os.path.join("in", title, "forbidden.csv"), skipinitialspace=True
    )
    required = pd.read_csv(
        os.path.join("in", title, "required.csv"), skipinitialspace=True
    )
    odm_journeys = pd.read_csv(os.path.join("out", title, "odm_journeys.csv"))
    pt_threshold = pd.read_csv(os.path.join("out", title, "pt_threshold.csv"))
    odm_threshold = pd.read_csv(os.path.join("out", title, "odm_threshold.csv"))

    forbidden_violations = {"time": [], "cost": []}
    required_violations = {"time": [], "cost": []}
    for j in odm_journeys.itertuples():
        below_threshold = (
            j.cost <= pt_threshold[pt_threshold["time"] == j.center].iat[0, 1]
            and j.cost <= odm_threshold[odm_threshold["time"] == j.center].iat[0, 1]
        )

        above_threshold = (
            j.cost > pt_threshold[pt_threshold["time"] == j.center].iat[0, 1]
            or j.cost > odm_threshold[odm_threshold["time"] == j.center].iat[0, 1]
        )

        if below_threshold and contains(forbidden, j):
            forbidden_violations["time"].append(j.center)
            forbidden_violations["cost"].append(j.cost)
        if above_threshold and contains(required, j):
            required_violations["time"].append(j.center)
            required_violations["cost"].append(j.cost)

    pd.DataFrame(forbidden_violations).to_csv(
        os.path.join("out", title, "forbidden_violations.csv"), index=False
    )
    pd.DataFrame(required_violations).to_csv(
        os.path.join("out", title, "required_violations.csv"), index=False
    )

    return forbidden_violations["time"] or required_violations["time"]
