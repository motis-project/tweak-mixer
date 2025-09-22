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

    blacklist_violations = []
    whitelist_violations = []
    for j in odm_journeys.itertuples():
        below_threshold = (
            j.cost < cost_threshold[cost_threshold["time"] == j.center].iat[0, 1]
        )

        print("below_threshold: {}, journeys: {}".format(below_threshold, j))

        if below_threshold and contains(blacklist, j):
            blacklist_violations.append()
            continue
        if (not below_threshold) and contains(whitelist, j):
            violation.append("whitelist")
            continue
        violation.append("none")

    odm_journeys["violation"] = violation
    odm_journeys.to_csv(os.path.join("out", title, "odm_journeys.csv"))
