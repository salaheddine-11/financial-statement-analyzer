import pandas as pd
from src.bilan import compute_bilan_comptable


def compute_bilan_financier(mapped_trial_balance):
    """
    Compute Moroccan Bilan Financier (Restructured Financial Balance Sheet).

    Applies standard Moroccan retraitements:
    1. Elimination of Non-Valeurs (Class 21) from Capital & Asset Net values.
    2. Adjustments for financial equilibrium analysis.

    Returns a DataFrame comparing Bilan Comptable vs Bilan Financier.
    """
    df_actif, df_passif = compute_bilan_comptable(mapped_trial_balance)
    years = sorted(mapped_trial_balance["year"].unique())

    rows = []

    for yr in years:
        sub_act = df_actif[df_actif["year"] == yr]
        sub_pas = df_passif[df_passif["year"] == yr]

        non_valeurs = sub_act[sub_act["rubrique"] == "Immobilisations en non-valeurs"]["net"].values[0]
        immob_net = sub_act[sub_act["rubrique"] == "TOTAL I - ACTIF IMMOBILISE"]["net"].values[0]
        circ_net = sub_act[sub_act["rubrique"] == "TOTAL II - ACTIF CIRCULANT HT"]["net"].values[0]
        tres_net = sub_act[sub_act["rubrique"] == "TOTAL III - TRESORERIE ACTIF"]["net"].values[0]

        capitaux_propres = sub_pas[sub_pas["rubrique"] == "Capitaux propres"]["montant"].values[0]
        fin_perm = sub_pas[sub_pas["rubrique"] == "TOTAL I - FINANCEMENT PERMANENT"]["montant"].values[0]
        passif_circ = sub_pas[sub_pas["rubrique"] == "TOTAL II - PASSIF CIRCULANT HT"]["montant"].values[0]
        tres_passif = sub_pas[sub_pas["rubrique"] == "TOTAL III - TRESORERIE PASSIF"]["montant"].values[0]

        # Financial Restatements:
        # 1. Eliminate Non-Valeurs from Actif Immobilisé & Capitaux Propres
        immob_financier = immob_net - non_valeurs
        capitaux_propres_financiers = capitaux_propres - non_valeurs
        fin_perm_financier = fin_perm - non_valeurs

        total_actif_financier = immob_financier + circ_net + tres_net
        total_passif_financier = fin_perm_financier + passif_circ + tres_passif

        # Financial FRF
        frf_financier = fin_perm_financier - immob_financier

        rows.extend([
            {"year": yr, "rubrique": "Actif Immobilisé Financier (hors Non-Valeurs)", "comptable": immob_net, "retraitement": -non_valeurs, "financier": immob_financier},
            {"year": yr, "rubrique": "Actif Circulant HT Net", "comptable": circ_net, "retraitement": 0, "financier": circ_net},
            {"year": yr, "rubrique": "Trésorerie Actif Net", "comptable": tres_net, "retraitement": 0, "financier": tres_net},
            {"year": yr, "rubrique": "TOTAL ACTIF FINANCIER", "comptable": immob_net + circ_net + tres_net, "retraitement": -non_valeurs, "financier": total_actif_financier},

            {"year": yr, "rubrique": "Capitaux Propres Net (hors Non-Valeurs)", "comptable": capitaux_propres, "retraitement": -non_valeurs, "financier": capitaux_propres_financiers},
            {"year": yr, "rubrique": "Financement Permanent Financier", "comptable": fin_perm, "retraitement": -non_valeurs, "financier": fin_perm_financier},
            {"year": yr, "rubrique": "Passif Circulant HT", "comptable": passif_circ, "retraitement": 0, "financier": passif_circ},
            {"year": yr, "rubrique": "Trésorerie Passif", "comptable": tres_passif, "retraitement": 0, "financier": tres_passif},
            {"year": yr, "rubrique": "TOTAL PASSIF FINANCIER", "comptable": fin_perm + passif_circ + tres_passif, "retraitement": -non_valeurs, "financier": total_passif_financier},
            {"year": yr, "rubrique": "FRF FINANCIER (Fin.Perm - Immob.Financier)", "comptable": fin_perm - immob_net, "retraitement": 0, "financier": frf_financier},
        ])

    return pd.DataFrame(rows)
