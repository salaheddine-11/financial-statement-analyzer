import os
import pandas as pd
import yaml

DEFAULT_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "config", "pcge_mapping.yaml")
)


def load_mapping_rules(path=None):
    """
    Load PCGM mapping rules from YAML configuration.
    """
    if path is None:
        path = DEFAULT_CONFIG_PATH

    with open(path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    rules = config.get("mapping_rules", config.get("balance_sheet", []))
    return rules


def mapping_rules_to_dataframe(rules):
    """
    Convert mapping rules into a pandas DataFrame for display.
    """
    df = pd.DataFrame(rules)
    if "prefix" in df.columns:
        df["prefix"] = df["prefix"].astype(str)
    return df


def find_matching_rule(account_code, rules):
    """
    Find the best matching mapping rule for an account code.
    Longest matching prefix wins.
    """
    account_code = str(account_code).strip()
    if account_code.endswith(".0"):
        account_code = account_code[:-2]

    best_rule = None
    best_prefix_length = -1

    for rule in rules:
        prefix = str(rule.get("prefix", "")).strip()
        if account_code.startswith(prefix):
            if len(prefix) > best_prefix_length:
                best_rule = rule
                best_prefix_length = len(prefix)

    return best_rule


def preview_account_coverage(trial_balance, rules):
    """
    Preview which trial balance accounts are mapped.
    """
    accounts = (
        trial_balance[["account_code", "account_label"]]
        .drop_duplicates()
        .copy()
    )

    matches = accounts["account_code"].apply(
        lambda code: find_matching_rule(code, rules)
    )

    accounts["matched_prefix"] = [
        match.get("prefix") if match else None for match in matches
    ]
    accounts["statement"] = [
        match.get("statement") if match else None for match in matches
    ]
    accounts["side"] = [
        match.get("side") if match else None for match in matches
    ]
    accounts["mass"] = [
        match.get("mass") if match else None for match in matches
    ]
    accounts["category"] = [
        match.get("category") if match else None for match in matches
    ]
    accounts["mapped"] = accounts["category"].notna()

    return accounts


def _calculate_normal_amount(row):
    """
    Calculate normal amount based on the account's normal side.

    Debit side: debit - credit
    Credit side: credit - debit
    """
    if row.get("normal_side") == "credit":
        return row["credit"] - row["debit"]
    return row["debit"] - row["credit"]


def map_trial_balance(trial_balance, rules):
    """
    Map each trial balance row to a PCGM financial category.
    """
    mapped = trial_balance.copy()

    matches = mapped["account_code"].apply(
        lambda code: find_matching_rule(code, rules)
    )

    mapped["matched_prefix"] = [
        match.get("prefix") if match else None for match in matches
    ]
    mapped["statement"] = [
        match.get("statement") if match else None for match in matches
    ]
    mapped["side"] = [
        match.get("side") if match else None for match in matches
    ]
    mapped["mass"] = [
        match.get("mass") if match else None for match in matches
    ]
    mapped["category"] = [
        match.get("category") if match else None for match in matches
    ]
    mapped["normal_side"] = [
        match.get("normal_side") if match else None for match in matches
    ]
    mapped["is_fictitious_asset"] = [
        bool(match.get("is_fictitious_asset", False)) if match else False
        for match in matches
    ]
    mapped["is_contra_asset"] = [
        bool(match.get("is_contra_asset", False)) if match else False
        for match in matches
    ]

    mapped["mapped"] = mapped["category"].notna()
    mapped["debit_credit_difference"] = mapped["debit"] - mapped["credit"]
    mapped["normal_amount"] = mapped.apply(_calculate_normal_amount, axis=1)

    return mapped


def get_unmapped_accounts(mapped_trial_balance):
    """
    Return accounts that could not be mapped.
    """
    columns = ["year", "account_code", "account_label", "debit", "credit"]
    unmapped = mapped_trial_balance.loc[
        mapped_trial_balance["mapped"] == False, columns
    ]
    unmapped = unmapped.drop_duplicates().reset_index(drop=True)
    return unmapped


def summarize_mapped_amounts(mapped_trial_balance):
    """
    Summarize mapped amounts by year, statement, side, mass, and category.
    """
    mapped_only = mapped_trial_balance[
        mapped_trial_balance["mapped"] == True
    ].copy()

    summary = (
        mapped_only.groupby(
            ["year", "statement", "mass", "category"], as_index=False
        )["normal_amount"]
        .sum()
    )

    summary = summary.sort_values(
        ["year", "statement", "mass", "category"]
    ).reset_index(drop=True)

    return summary