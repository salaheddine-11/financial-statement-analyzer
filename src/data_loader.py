import pandas as pd

REQUIRED_COLUMNS = {
    "year",
    "account_code",
    "account_label",
    "debit",
    "credit"
}


def load_trial_balance(source):
    """
    Load a trial balance CSV file.

    Expected columns:
    year, account_code, account_label, debit, credit
    """

    df = pd.read_csv(source)

    # Clean column names
    df.columns = [column.strip().lower() for column in df.columns]

    # Check required columns
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Convert numeric columns
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["debit"] = pd.to_numeric(df["debit"], errors="coerce")
    df["credit"] = pd.to_numeric(df["credit"], errors="coerce")

    # Clean text columns
    df["account_code"] = df["account_code"].astype(str).str.strip()
    df["account_label"] = df["account_label"].astype(str).str.strip()

    # Drop rows without year or account code
    df = df.dropna(subset=["year", "account_code"])

    # Replace missing amounts with zero
    df["debit"] = df["debit"].fillna(0)
    df["credit"] = df["credit"].fillna(0)

    # Keep only non-negative amounts
    df = df[(df["debit"] >= 0) & (df["credit"] >= 0)]

    # Convert year to integer
    df["year"] = df["year"].astype(int)

    return df