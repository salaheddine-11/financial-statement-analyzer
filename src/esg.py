import pandas as pd


def compute_esg(mapped_trial_balance):
    """
    Compute official Moroccan État des Soldes de Gestion (ESG) & CAF by year.

    Returns a tuple of DataFrames: (df_tfr, df_caf)
    """
    tb = mapped_trial_balance.copy()
    tb["account_code"] = tb["account_code"].astype(str).str.strip()

    years = sorted(tb["year"].unique())
    tfr_rows = []
    caf_rows = []

    for yr in years:
        sub = tb[tb["year"] == yr]

        def get_credit(prefixes):
            matched = sub[sub["account_code"].str.startswith(tuple(prefixes))]
            return matched["credit"].sum() - matched["debit"].sum()

        def get_debit(prefixes):
            matched = sub[sub["account_code"].str.startswith(tuple(prefixes))]
            return matched["debit"].sum() - matched["credit"].sum()

        # ----------------------------------------------------
        # 1. TABLEAU DE FORMATION DU RESULTAT (TFR)
        # ----------------------------------------------------
        ventes_mches = get_credit(["711"])
        achats_mches = get_debit(["611"])
        marge_brute = ventes_mches - achats_mches

        ventes_prod = get_credit(["712"])
        var_stocks_prod = get_credit(["713"])
        immob_prod = get_credit(["714"])
        production_exercice = ventes_prod + var_stocks_prod + immob_prod

        achats_mat = get_debit(["612"])
        autres_charges_ext = get_debit(["613", "614"])
        consommation_exercice = achats_mat + autres_charges_ext

        valeur_ajoutee = marge_brute + production_exercice - consommation_exercice

        subv_expl = get_credit(["716"])
        impots_taxes = get_debit(["616"])
        charges_personnel = get_debit(["617"])

        ebe = valeur_ajoutee + subv_expl - impots_taxes - charges_personnel

        autres_prod_expl = get_credit(["718"])
        reprises_expl = get_credit(["719"])
        autres_charg_expl = get_debit(["618"])
        dotations_expl = get_debit(["619"])

        rex = ebe + autres_prod_expl + reprises_expl - autres_charg_expl - dotations_expl

        prod_fin = get_credit(["73"])
        charg_fin = get_debit(["63"])
        resultat_financier = prod_fin - charg_fin

        resultat_courant = rex + resultat_financier

        prod_nc = get_credit(["75"])
        charg_nc = get_debit(["65"])
        resultat_non_courant = prod_nc - charg_nc

        impots_res = get_debit(["670"])
        resultat_net = resultat_courant + resultat_non_courant - impots_res

        tfr_rows.extend([
            {"year": yr, "indicateur": "1. Marge brute sur ventes en l'état", "valeur": marge_brute},
            {"year": yr, "indicateur": "2. Production de l'exercice", "valeur": production_exercice},
            {"year": yr, "indicateur": "3. Consommation de l'exercice", "valeur": consommation_exercice},
            {"year": yr, "indicateur": "4. VALEUR AJOUTEE (VA)", "valeur": valeur_ajoutee},
            {"year": yr, "indicateur": "5. EXCEDENT BRUT D'EXPLOITATION (EBE)", "valeur": ebe},
            {"year": yr, "indicateur": "6. RESULTAT D'EXPLOITATION (REX)", "valeur": rex},
            {"year": yr, "indicateur": "7. RESULTAT FINANCIER", "valeur": resultat_financier},
            {"year": yr, "indicateur": "8. RESULTAT COURANT", "valeur": resultat_courant},
            {"year": yr, "indicateur": "9. RESULTAT NON COURANT", "valeur": resultat_non_courant},
            {"year": yr, "indicateur": "10. RESULTAT NET DE L'EXERCICE", "valeur": resultat_net},
        ])

        # ----------------------------------------------------
        # 2. CAPACITE D'AUTOFINANCEMENT (CAF)
        # ----------------------------------------------------
        # Dotations
        dotations_immob = get_debit(["6191", "6192", "6193"])
        dotations_fin_durable = get_debit(["6392", "6393"])
        dotations_nc_durable = get_debit(["6591", "6594", "6595"])
        total_dotations = dotations_immob + dotations_fin_durable + dotations_nc_durable

        # Reprises
        reprises_immob = get_credit(["7191", "7192", "7193"])
        reprises_fin_durable = get_credit(["7392", "7393"])
        reprises_nc_durable = get_credit(["7591", "7594", "7595"])
        reprises_subv_invest = get_credit(["757"])
        total_reprises = reprises_immob + reprises_fin_durable + reprises_nc_durable + reprises_subv_invest

        # Cessions d'immobilisations
        vna_immob_cedees = get_debit(["651"])
        prod_cessions = get_credit(["751"])

        caf = (
            resultat_net
            + total_dotations
            - total_reprises
            + vna_immob_cedees
            - prod_cessions
        )

        caf_rows.extend([
            {"year": yr, "element": "Résultat net de l'exercice", "montant": resultat_net},
            {"year": yr, "element": "+ Dotations de l'exercice (hors circulant/trésorerie)", "montant": total_dotations},
            {"year": yr, "element": "- Reprises de l'exercice (hors circulant/trésorerie)", "montant": total_reprises},
            {"year": yr, "element": "+ VNA des immobilisations cédées", "montant": vna_immob_cedees},
            {"year": yr, "element": "- Produits des cessions d'immobilisations", "montant": prod_cessions},
            {"year": yr, "element": "= CAPACITE D'AUTOFINANCEMENT (CAF)", "montant": caf},
        ])

    return pd.DataFrame(tfr_rows), pd.DataFrame(caf_rows)
