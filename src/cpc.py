import pandas as pd


def compute_cpc(mapped_trial_balance):
    """
    Compute official Moroccan Compte de Produits et Charges (CPC) by year.

    Returns a DataFrame containing the detailed CPC statement.
    """
    tb = mapped_trial_balance.copy()
    tb["account_code"] = tb["account_code"].astype(str).str.strip()

    years = sorted(tb["year"].unique())
    cpc_rows = []

    for yr in years:
        sub = tb[tb["year"] == yr]

        def get_credit_minus_debit(prefixes):
            matched = sub[sub["account_code"].str.startswith(tuple(prefixes))]
            return matched["credit"].sum() - matched["debit"].sum()

        def get_debit_minus_credit(prefixes):
            matched = sub[sub["account_code"].str.startswith(tuple(prefixes))]
            return matched["debit"].sum() - matched["credit"].sum()

        # ----------------------------------------------------
        # I. EXPLOITATION
        # ----------------------------------------------------
        ventes_marchandises = get_credit_minus_debit(["711"])
        ventes_biens_services = get_credit_minus_debit(["712"])
        variation_stocks_prod = get_credit_minus_debit(["713"])
        immob_produites = get_credit_minus_debit(["714"])
        subventions_expl = get_credit_minus_debit(["716"])
        autres_prod_expl = get_credit_minus_debit(["718"])
        reprises_expl = get_credit_minus_debit(["719"])

        total_prod_expl = (
            ventes_marchandises
            + ventes_biens_services
            + variation_stocks_prod
            + immob_produites
            + subventions_expl
            + autres_prod_expl
            + reprises_expl
        )

        achats_revendus_mches = get_debit_minus_credit(["611"])
        achats_consommes_mat = get_debit_minus_credit(["612"])
        autres_charges_ext = get_debit_minus_credit(["613", "614"])
        impots_et_taxes = get_debit_minus_credit(["616"])
        charges_personnel = get_debit_minus_credit(["617"])
        autres_charges_expl = get_debit_minus_credit(["618"])
        dotations_expl = get_debit_minus_credit(["619"])

        total_charg_expl = (
            achats_revendus_mches
            + achats_consommes_mat
            + autres_charges_ext
            + impots_et_taxes
            + charges_personnel
            + autres_charges_expl
            + dotations_expl
        )

        resultat_exploitation = total_prod_expl - total_charg_expl

        # ----------------------------------------------------
        # II. FINANCIER
        # ----------------------------------------------------
        prod_titres = get_credit_minus_debit(["732"])
        gains_change = get_credit_minus_debit(["733"])
        interets_prod_fin = get_credit_minus_debit(["738"])
        reprises_fin = get_credit_minus_debit(["739"])

        total_prod_fin = prod_titres + gains_change + interets_prod_fin + reprises_fin

        charges_interets = get_debit_minus_credit(["631"])
        pertes_change = get_debit_minus_credit(["633"])
        autres_charg_fin = get_debit_minus_credit(["638"])
        dotations_fin = get_debit_minus_credit(["639"])

        total_charg_fin = charges_interets + pertes_change + autres_charg_fin + dotations_fin

        resultat_financier = total_prod_fin - total_charg_fin

        # RESULTAT COURANT
        resultat_courant = resultat_exploitation + resultat_financier

        # ----------------------------------------------------
        # III. NON COURANT
        # ----------------------------------------------------
        prod_cessions_immob = get_credit_minus_debit(["751"])
        subventions_equilibre = get_credit_minus_debit(["756"])
        reprises_subv_invest = get_credit_minus_debit(["757"])
        autres_prod_nc = get_credit_minus_debit(["758"])
        reprises_nc = get_credit_minus_debit(["759"])

        total_prod_nc = (
            prod_cessions_immob
            + subventions_equilibre
            + reprises_subv_invest
            + autres_prod_nc
            + reprises_nc
        )

        vna_immob_cedees = get_debit_minus_credit(["651"])
        subventions_accordees = get_debit_minus_credit(["656"])
        autres_charg_nc = get_debit_minus_credit(["658"])
        dotations_nc = get_debit_minus_credit(["659"])

        total_charg_nc = (
            vna_immob_cedees
            + subventions_accordees
            + autres_charg_nc
            + dotations_nc
        )

        resultat_non_courant = total_prod_nc - total_charg_nc

        # RESULTAT AVANT IMPOTS
        resultat_avant_impots = resultat_courant + resultat_non_courant

        # IMPOTS SUR LES RESULTATS
        impots_resultats = get_debit_minus_credit(["670"])

        # RESULTAT NET
        resultat_net = resultat_avant_impots - impots_resultats

        cpc_rows.extend([
            {"year": yr, "section": "I. PRODUITS D'EXPLOITATION", "rubrique": "Ventes de marchandises", "montant": ventes_marchandises},
            {"year": yr, "section": "I. PRODUITS D'EXPLOITATION", "rubrique": "Ventes de biens et services produits", "montant": ventes_biens_services},
            {"year": yr, "section": "I. PRODUITS D'EXPLOITATION", "rubrique": "Variation des stocks de produits", "montant": variation_stocks_prod},
            {"year": yr, "section": "I. PRODUITS D'EXPLOITATION", "rubrique": "Autres produits & reprises d'exploitation", "montant": subventions_expl + autres_prod_expl + reprises_expl},
            {"year": yr, "section": "I. PRODUITS D'EXPLOITATION", "rubrique": "TOTAL I - PRODUITS D'EXPLOITATION", "montant": total_prod_expl},

            {"year": yr, "section": "II. CHARGES D'EXPLOITATION", "rubrique": "Achats revendus de marchandises", "montant": achats_revendus_mches},
            {"year": yr, "section": "II. CHARGES D'EXPLOITATION", "rubrique": "Achats consommés de matières et fournitures", "montant": achats_consommes_mat},
            {"year": yr, "section": "II. CHARGES D'EXPLOITATION", "rubrique": "Autres charges externes", "montant": autres_charges_ext},
            {"year": yr, "section": "II. CHARGES D'EXPLOITATION", "rubrique": "Impôts et taxes", "montant": impots_et_taxes},
            {"year": yr, "section": "II. CHARGES D'EXPLOITATION", "rubrique": "Charges de personnel", "montant": charges_personnel},
            {"year": yr, "section": "II. CHARGES D'EXPLOITATION", "rubrique": "Dotations d'exploitation", "montant": dotations_expl},
            {"year": yr, "section": "II. CHARGES D'EXPLOITATION", "rubrique": "TOTAL II - CHARGES D'EXPLOITATION", "montant": total_charg_expl},

            {"year": yr, "section": "RESULTAT D'EXPLOITATION", "rubrique": "III. RESULTAT D'EXPLOITATION (I - II)", "montant": resultat_exploitation},

            {"year": yr, "section": "III. PRODUITS FINANCIERS", "rubrique": "Intérêts, gains de change & prod. fin.", "montant": total_prod_fin},
            {"year": yr, "section": "III. PRODUITS FINANCIERS", "rubrique": "TOTAL IV - PRODUITS FINANCIERS", "montant": total_prod_fin},

            {"year": yr, "section": "IV. CHARGES FINANCIERES", "rubrique": "Charges d'intérêts & losses change", "montant": total_charg_fin},
            {"year": yr, "section": "IV. CHARGES FINANCIERES", "rubrique": "TOTAL V - CHARGES FINANCIERES", "montant": total_charg_fin},

            {"year": yr, "section": "RESULTAT FINANCIER", "rubrique": "VI. RESULTAT FINANCIER (IV - V)", "montant": resultat_financier},
            {"year": yr, "section": "RESULTAT COURANT", "rubrique": "VII. RESULTAT COURANT (III + VI)", "montant": resultat_courant},

            {"year": yr, "section": "V. PRODUITS NON COURANTS", "rubrique": "TOTAL VIII - PRODUITS NON COURANTS", "montant": total_prod_nc},
            {"year": yr, "section": "VI. CHARGES NON COURANTES", "rubrique": "TOTAL IX - CHARGES NON COURANTES", "montant": total_charg_nc},

            {"year": yr, "section": "RESULTAT NON COURANT", "rubrique": "X. RESULTAT NON COURANT (VIII - IX)", "montant": resultat_non_courant},
            {"year": yr, "section": "RESULTAT AVANT IMPOTS", "rubrique": "XI. RESULTAT AVANT IMPOTS (VII + X)", "montant": resultat_avant_impots},

            {"year": yr, "section": "IMPOTS SUR LES RESULTATS", "rubrique": "XII. IMPOTS SUR LES RESULTATS", "montant": impots_resultats},
            {"year": yr, "section": "RESULTAT NET", "rubrique": "XIII. RESULTAT NET (XI - XII)", "montant": resultat_net},
        ])

    return pd.DataFrame(cpc_rows)
