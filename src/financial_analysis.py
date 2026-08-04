import pandas as pd
from src.bilan import compute_bilan_comptable
from src.esg import compute_esg


def compute_financial_analysis(mapped_trial_balance):
    """
    Compute Moroccan Financial Equilibrium (FRF, BFR, TN) and key ratios.

    Returns a tuple of DataFrames: (df_equilibrium, df_ratios)
    """
    df_actif, df_passif = compute_bilan_comptable(mapped_trial_balance)
    df_tfr, df_caf = compute_esg(mapped_trial_balance)

    years = sorted(mapped_trial_balance["year"].unique())
    eq_rows = []
    ratio_rows = []

    for yr in years:
        sub_act = df_actif[df_actif["year"] == yr]
        sub_pas = df_passif[df_passif["year"] == yr]

        # Extract aggregates
        actif_immob_net = sub_act[sub_act["rubrique"] == "TOTAL I - ACTIF IMMOBILISE"]["net"].values[0]
        actif_circ_net = sub_act[sub_act["rubrique"] == "TOTAL II - ACTIF CIRCULANT HT"]["net"].values[0]
        tres_actif_net = sub_act[sub_act["rubrique"] == "TOTAL III - TRESORERIE ACTIF"]["net"].values[0]
        total_actif_net = sub_act[sub_act["rubrique"] == "TOTAL GENERAL ACTIF (I + II + III)"]["net"].values[0]

        fin_perm = sub_pas[sub_pas["rubrique"] == "TOTAL I - FINANCEMENT PERMANENT"]["montant"].values[0]
        passif_circ = sub_pas[sub_pas["rubrique"] == "TOTAL II - PASSIF CIRCULANT HT"]["montant"].values[0]
        tres_passif = sub_pas[sub_pas["rubrique"] == "TOTAL III - TRESORERIE PASSIF"]["montant"].values[0]
        
        capitaux_propres = sub_pas[sub_pas["rubrique"] == "Capitaux propres"]["montant"].values[0]
        dettes_financement = sub_pas[sub_pas["rubrique"] == "Dettes de financement"]["montant"].values[0]

        # Financial Equilibrium Indicators
        frf = fin_perm - actif_immob_net
        bfr = actif_circ_net - passif_circ
        tn_from_eq = frf - bfr
        tn_from_cash = tres_actif_net - tres_passif

        eq_rows.extend([
            {"year": yr, "indicator": "Financement Permanent", "value": fin_perm},
            {"year": yr, "indicator": "Actif Immobilisé Net", "value": actif_immob_net},
            {"year": yr, "indicator": "1. FONDS DE ROULEMENT FONCTIONNEL (FRF)", "value": frf},
            {"year": yr, "indicator": "Actif Circulant HT Net", "value": actif_circ_net},
            {"year": yr, "indicator": "Passif Circulant HT", "value": passif_circ},
            {"year": yr, "indicator": "2. BESOIN EN FONDS DE ROULEMENT (BFR)", "value": bfr},
            {"year": yr, "indicator": "Trésorerie Actif Net", "value": tres_actif_net},
            {"year": yr, "indicator": "Trésorerie Passif", "value": tres_passif},
            {"year": yr, "indicator": "3. TRESORERIE NETTE (TN = FRF - BFR)", "value": tn_from_eq},
        ])

        # Ratios
        total_dettes = dettes_financement + passif_circ + tres_passif

        autonomie_fin = (capitaux_propres / fin_perm) if fin_perm > 0 else 0
        solvabilite_gen = (total_actif_net / total_dettes) if total_dettes > 0 else 0
        liquidite_gen = ((actif_circ_net + tres_actif_net) / (passif_circ + tres_passif)) if (passif_circ + tres_passif) > 0 else 0
        liquidite_imm = (tres_actif_net / (passif_circ + tres_passif)) if (passif_circ + tres_passif) > 0 else 0

        # Profitability from TFR
        resultat_net = df_tfr[(df_tfr["year"] == yr) & (df_tfr["indicateur"] == "10. RESULTAT NET DE L'EXERCICE")]["valeur"].values[0]
        rex = df_tfr[(df_tfr["year"] == yr) & (df_tfr["indicateur"] == "6. RESULTAT D'EXPLOITATION (REX)")]["valeur"].values[0]

        roe = (resultat_net / capitaux_propres) if capitaux_propres > 0 else 0
        roa = (rex / total_actif_net) if total_actif_net > 0 else 0

        ratio_rows.extend([
            {"year": yr, "category": "Structure Financière", "ratio_name": "Autonomie Financière (CP / Fin. Perm.)", "value": autonomie_fin, "unit": "%", "norm": ">= 50%"},
            {"year": yr, "category": "Structure Financière", "ratio_name": "Solvabilité Générale (Actif / Dettes)", "value": solvabilite_gen, "unit": "x", "norm": "> 1.0x"},
            {"year": yr, "category": "Liquidité", "ratio_name": "Liquidité Générale ((Circ+Trés) / Passif.Circ)", "value": liquidite_gen, "unit": "x", "norm": ">= 1.0x"},
            {"year": yr, "category": "Liquidité", "ratio_name": "Liquidité Immédiate (Trés.Actif / Passif.Circ)", "value": liquidite_imm, "unit": "x", "norm": "> 0.2x"},
            {"year": yr, "category": "Rentabilité", "ratio_name": "Rentabilité Financière (ROE = RN / CP)", "value": roe, "unit": "%", "norm": "> 10%"},
            {"year": yr, "category": "Rentabilité", "ratio_name": "Rentabilité Économique (ROA = REX / Actif)", "value": roa, "unit": "%", "norm": "> 5%"},
        ])

    return pd.DataFrame(eq_rows), pd.DataFrame(ratio_rows)
