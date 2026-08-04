import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import load_trial_balance
from src.validation import validate_trial_balance
from src.pcge_mapper import load_mapping_rules, map_trial_balance, get_unmapped_accounts
from src.bilan import compute_bilan_comptable
from src.cpc import compute_cpc
from src.esg import compute_esg
from src.financial_analysis import compute_financial_analysis
from src.retraitements import compute_bilan_financier


def test_load_and_validate_trial_balance():
    tb = load_trial_balance("data/sample_trial_balance.csv")
    assert not tb.empty
    assert set(tb["year"].unique()) == {2021, 2022, 2023}

    val = validate_trial_balance(tb)
    assert val["balanced"].all()


def test_mapping_coverage():
    tb = load_trial_balance("data/sample_trial_balance.csv")
    rules = load_mapping_rules()
    mapped = map_trial_balance(tb, rules)

    unmapped = get_unmapped_accounts(mapped)
    assert unmapped.empty, f"Unmapped accounts found: {unmapped}"


def test_bilan_identity():
    tb = load_trial_balance("data/sample_trial_balance.csv")
    rules = load_mapping_rules()
    mapped = map_trial_balance(tb, rules)

    df_actif, df_passif = compute_bilan_comptable(mapped)

    for yr in [2021, 2022, 2023]:
        total_actif = df_actif[(df_actif["year"] == yr) & (df_actif["rubrique"] == "TOTAL GENERAL ACTIF (I + II + III)")]["net"].values[0]
        total_passif = df_passif[(df_passif["year"] == yr) & (df_passif["rubrique"] == "TOTAL GENERAL PASSIF (I + II + III)")]["montant"].values[0]

        assert abs(total_actif - total_passif) < 0.01, f"Year {yr}: Total Actif ({total_actif}) != Total Passif ({total_passif})"


def test_cpc_and_esg_coherence():
    tb = load_trial_balance("data/sample_trial_balance.csv")
    rules = load_mapping_rules()
    mapped = map_trial_balance(tb, rules)

    df_cpc = compute_cpc(mapped)
    df_tfr, df_caf = compute_esg(mapped)
    df_actif, df_passif = compute_bilan_comptable(mapped)

    for yr in [2021, 2022, 2023]:
        rn_cpc = df_cpc[(df_cpc["year"] == yr) & (df_cpc["rubrique"] == "XIII. RESULTAT NET (XI - XII)")]["montant"].values[0]
        rn_esg = df_tfr[(df_tfr["year"] == yr) & (df_tfr["indicateur"] == "10. RESULTAT NET DE L'EXERCICE")]["valeur"].values[0]
        rn_bilan = df_passif[(df_passif["year"] == yr) & (df_passif["rubrique"] == "  - Résultat net de l'exercice")]["montant"].values[0]

        assert abs(rn_cpc - rn_esg) < 0.01, f"Year {yr}: CPC RN ({rn_cpc}) != ESG RN ({rn_esg})"
        assert abs(rn_cpc - rn_bilan) < 0.01, f"Year {yr}: CPC RN ({rn_cpc}) != Bilan RN ({rn_bilan})"


def test_financial_equilibrium_coherence():
    tb = load_trial_balance("data/sample_trial_balance.csv")
    rules = load_mapping_rules()
    mapped = map_trial_balance(tb, rules)

    df_eq, df_ratios = compute_financial_analysis(mapped)

    for yr in [2021, 2022, 2023]:
        frf = df_eq[(df_eq["year"] == yr) & (df_eq["indicator"] == "1. FONDS DE ROULEMENT FONCTIONNEL (FRF)")]["value"].values[0]
        bfr = df_eq[(df_eq["year"] == yr) & (df_eq["indicator"] == "2. BESOIN EN FONDS DE ROULEMENT (BFR)")]["value"].values[0]
        tn = df_eq[(df_eq["year"] == yr) & (df_eq["indicator"] == "3. TRESORERIE NETTE (TN = FRF - BFR)")]["value"].values[0]

        assert abs(tn - (frf - bfr)) < 0.01, f"Year {yr}: TN ({tn}) != FRF - BFR ({frf - bfr})"


if __name__ == "__main__":
    test_load_and_validate_trial_balance()
    test_mapping_coverage()
    test_bilan_identity()
    test_cpc_and_esg_coherence()
    test_financial_equilibrium_coherence()
    print("ALL TESTS PASSED SUCCESSFULLY!")


