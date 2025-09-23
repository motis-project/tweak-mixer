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
    blacklist = pd.read_csv(
        os.path.join("in", title, "blacklist.csv"), skipinitialspace=True
    )
    whitelist = pd.read_csv(
        os.path.join("in", title, "whitelist.csv"), skipinitialspace=True
    )
    odm_journeys = pd.read_csv(os.path.join("out", title, "odm_journeys.csv"))
    cost_threshold = pd.read_csv(os.path.join("out", title, "cost_threshold.csv"))

    blacklist_violations = {"time": [], "cost": []}
    whitelist_violations = {"time": [], "cost": []}
    for j in odm_journeys.itertuples():
        below_threshold = (
            j.cost < cost_threshold[cost_threshold["time"] == j.center].iat[0, 1]
        )

        if below_threshold and contains(blacklist, j):
            blacklist_violations["time"].append(j.center)
            blacklist_violations["cost"].append(j.cost)
        if (not below_threshold) and contains(whitelist, j):
            whitelist_violations["time"].append(j.center)
            whitelist_violations["cost"].append(j.cost)

    pd.DataFrame(blacklist_violations).to_csv(
        os.path.join("out", title, "blacklist_violations.csv"), index=False
    )
    pd.DataFrame(whitelist_violations).to_csv(
        os.path.join("out", title, "whitelist_violations.csv"), index=False
    )

    return blacklist_violations["time"] or whitelist_violations["time"]
