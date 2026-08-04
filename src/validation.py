import pandas as pd


def validate_trial_balance(trial_balance):
    """
    Check whether the trial balance is balanced by year.

    Rule:
    Total debit must equal total credit.
    """

    summary = (
        trial_balance
        .groupby("year", as_index=False)[["debit", "credit"]]
        .sum()
    )

    summary["difference"] = summary["debit"] - summary["credit"]
    summary["balanced"] = summary["difference"].abs() < 0.01

    return summary