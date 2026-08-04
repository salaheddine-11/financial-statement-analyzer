import pandas as pd
import yaml

CONFIG_PATH = "config/pcge_mapping.yaml"


def load_mapping_rules(path=CONFIG_PATH):
    """
    Load PCGE mapping rules from YAML configuration.
    """

    with open(path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    rules = config.get("balance_sheet", [])

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

    The longest matching prefix wins.
    """

    account_code = str(account_code).strip()

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
        match.get("prefix") if match else None
        for match in matches
    ]

    accounts["category"] = [
        match.get("category") if match else None
        for match in matches
    ]

    accounts["mass"] = [
        match.get("mass") if match else None
        for match in matches
    ]

    accounts["mapped"] = accounts["category"].notna()

    return accounts