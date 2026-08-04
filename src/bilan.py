import pandas as pd


def compute_bilan_comptable(mapped_trial_balance):
    """
    Compute official Moroccan Bilan Comptable (Balance Sheet) by year.

    Returns a tuple of two DataFrames: (df_actif, df_passif)
    """
    tb = mapped_trial_balance.copy()
    tb["account_code"] = tb["account_code"].astype(str).str.strip()

    years = sorted(tb["year"].unique())
    actif_rows = []
    passif_rows = []

    for yr in years:
        sub = tb[tb["year"] == yr]

        def sum_debit_credit(prefix, contra=False):
            matched = sub[sub["account_code"].str.startswith(tuple(prefix))]
            debit = matched["debit"].sum()
            credit = matched["credit"].sum()
            if contra:
                return credit - debit
            return debit - credit

        # ----------------------------------------------------
        # ACTIF
        # ----------------------------------------------------
        # I. Actif Immobilisé
        non_valeurs_brut = sum_debit_credit(["21"])
        incorporelles_brut = sum_debit_credit(["22"])
        corporelles_brut = sum_debit_credit(["23"])
        financieres_brut = sum_debit_credit(["24", "25"])
        ecart_conv_actif_lt = sum_debit_credit(["27"])
        amort_immobilisations = sum_debit_credit(["28"], contra=True)
        prov_immobilisations = sum_debit_credit(["29"], contra=True)

        total_immob_brut = (
            non_valeurs_brut
            + incorporelles_brut
            + corporelles_brut
            + financieres_brut
            + ecart_conv_actif_lt
        )
        total_immob_amort_prov = amort_immobilisations + prov_immobilisations
        total_immob_net = total_immob_brut - total_immob_amort_prov

        # II. Actif Circulant (HT)
        stocks_brut = sum_debit_credit(["31"])
        creances_brut = sum_debit_credit(["34"])
        tvp_brut = sum_debit_credit(["35"])
        ecart_conv_actif_circ = sum_debit_credit(["37"])
        prov_circulant = sum_debit_credit(["39"], contra=True)

        total_circ_brut = (
            stocks_brut + creances_brut + tvp_brut + ecart_conv_actif_circ
        )
        total_circ_prov = prov_circulant
        total_circ_net = total_circ_brut - total_circ_prov

        # III. Trésorerie Actif
        cheques_brut = sum_debit_credit(["511"])
        banques_brut = sum_debit_credit(["514"])
        caisse_brut = sum_debit_credit(["516"])
        prov_tresorerie = sum_debit_credit(["59"], contra=True)

        total_tres_brut = cheques_brut + banques_brut + caisse_brut
        total_tres_prov = prov_tresorerie
        total_tres_net = total_tres_brut - total_tres_prov

        total_actif_brut = total_immob_brut + total_circ_brut + total_tres_brut
        total_actif_amort_prov = total_immob_amort_prov + total_circ_prov + total_tres_prov
        total_actif_net = total_actif_brut - total_actif_amort_prov

        actif_rows.extend([
            {"year": yr, "mass": "I. ACTIF IMMOBILISE", "rubrique": "Immobilisations en non-valeurs", "brut": non_valeurs_brut, "amort_prov": 0, "net": non_valeurs_brut},
            {"year": yr, "mass": "I. ACTIF IMMOBILISE", "rubrique": "Immobilisations incorporelles", "brut": incorporelles_brut, "amort_prov": 0, "net": incorporelles_brut},
            {"year": yr, "mass": "I. ACTIF IMMOBILISE", "rubrique": "Immobilisations corporelles", "brut": corporelles_brut, "amort_prov": 0, "net": corporelles_brut},
            {"year": yr, "mass": "I. ACTIF IMMOBILISE", "rubrique": "Immobilisations financières", "brut": financieres_brut, "amort_prov": 0, "net": financieres_brut},
            {"year": yr, "mass": "I. ACTIF IMMOBILISE", "rubrique": "Amortissements & Provisions immo.", "brut": 0, "amort_prov": total_immob_amort_prov, "net": -total_immob_amort_prov},
            {"year": yr, "mass": "I. ACTIF IMMOBILISE", "rubrique": "TOTAL I - ACTIF IMMOBILISE", "brut": total_immob_brut, "amort_prov": total_immob_amort_prov, "net": total_immob_net},
            
            {"year": yr, "mass": "II. ACTIF CIRCULANT (HT)", "rubrique": "Stocks", "brut": stocks_brut, "amort_prov": 0, "net": stocks_brut},
            {"year": yr, "mass": "II. ACTIF CIRCULANT (HT)", "rubrique": "Créances de l'actif circulant", "brut": creances_brut, "amort_prov": 0, "net": creances_brut},
            {"year": yr, "mass": "II. ACTIF CIRCULANT (HT)", "rubrique": "Titres et valeurs de placement", "brut": tvp_brut, "amort_prov": 0, "net": tvp_brut},
            {"year": yr, "mass": "II. ACTIF CIRCULANT (HT)", "rubrique": "Provisions actif circulant", "brut": 0, "amort_prov": prov_circulant, "net": -prov_circulant},
            {"year": yr, "mass": "II. ACTIF CIRCULANT (HT)", "rubrique": "TOTAL II - ACTIF CIRCULANT HT", "brut": total_circ_brut, "amort_prov": total_circ_prov, "net": total_circ_net},

            {"year": yr, "mass": "III. TRESORERIE ACTIF", "rubrique": "Chèques et valeurs à encaisser", "brut": cheques_brut, "amort_prov": 0, "net": cheques_brut},
            {"year": yr, "mass": "III. TRESORERIE ACTIF", "rubrique": "Banques, TG et CP", "brut": banques_brut, "amort_prov": 0, "net": banques_brut},
            {"year": yr, "mass": "III. TRESORERIE ACTIF", "rubrique": "Caisse, régies", "brut": caisse_brut, "amort_prov": 0, "net": caisse_brut},
            {"year": yr, "mass": "III. TRESORERIE ACTIF", "rubrique": "TOTAL III - TRESORERIE ACTIF", "brut": total_tres_brut, "amort_prov": total_tres_prov, "net": total_tres_net},

            {"year": yr, "mass": "TOTAL GENERAL ACTIF", "rubrique": "TOTAL GENERAL ACTIF (I + II + III)", "brut": total_actif_brut, "amort_prov": total_actif_amort_prov, "net": total_actif_net},
        ])

        # ----------------------------------------------------
        # PASSIF
        # ----------------------------------------------------
        def sum_credit_debit(prefix):
            matched = sub[sub["account_code"].str.startswith(tuple(prefix))]
            return matched["credit"].sum() - matched["debit"].sum()

        capital_social = sum_credit_debit(["111"])
        primes_emission = sum_credit_debit(["112"])
        ecarts_reeval = sum_credit_debit(["113"])
        reserve_legale = sum_credit_debit(["114"])
        autres_reserves = sum_credit_debit(["115"])
        report_a_nouveau = sum_credit_debit(["116"])
        resultat_instance = sum_credit_debit(["118"])
        
        # Calculate CPC net result (Produits 7 - Charges 6)
        prod_total = sum_credit_debit(["7"])
        charg_total = sum_debit_credit(["6"])
        cpc_net_result = prod_total - charg_total

        # If account 1191 is explicitly posted, use it; otherwise use cpc_net_result
        posted_1191 = sum_credit_debit(["1191"])
        resultat_net = posted_1191 if posted_1191 != 0 else cpc_net_result

        capitaux_propres = (
            capital_social
            + primes_emission
            + ecarts_reeval
            + reserve_legale
            + autres_reserves
            + report_a_nouveau
            + resultat_instance
            + resultat_net
        )

        subventions_invest = sum_credit_debit(["131"])
        provisions_reglem = sum_credit_debit(["135"])
        capitaux_assimiles = subventions_invest + provisions_reglem

        dettes_financement = sum_credit_debit(["14"])
        provisions_durables = sum_credit_debit(["15"])
        ecarts_conv_passif_lt = sum_credit_debit(["17"])

        total_financement_permanent = (
            capitaux_propres
            + capitaux_assimiles
            + dettes_financement
            + provisions_durables
            + ecarts_conv_passif_lt
        )

        dettes_passif_circ = sum_credit_debit(["44"])
        autres_prov_risques = sum_credit_debit(["45"])
        ecart_conv_passif_circ = sum_credit_debit(["47"])

        total_passif_circulant = (
            dettes_passif_circ + autres_prov_risques + ecart_conv_passif_circ
        )

        credits_escompte = sum_credit_debit(["552"])
        credits_tresorerie = sum_credit_debit(["553"])
        banques_solde_crediteur = sum_credit_debit(["554", "559"])

        total_tresorerie_passif = (
            credits_escompte + credits_tresorerie + banques_solde_crediteur
        )

        total_general_passif = (
            total_financement_permanent
            + total_passif_circulant
            + total_tresorerie_passif
        )

        passif_rows.extend([
            {"year": yr, "mass": "I. FINANCEMENT PERMANENT", "rubrique": "Capitaux propres", "montant": capitaux_propres},
            {"year": yr, "mass": "I. FINANCEMENT PERMANENT", "rubrique": "  - Capital social ou personnel", "montant": capital_social},
            {"year": yr, "mass": "I. FINANCEMENT PERMANENT", "rubrique": "  - Réserve légale", "montant": reserve_legale},
            {"year": yr, "mass": "I. FINANCEMENT PERMANENT", "rubrique": "  - Autres réserves & Report à nouveau", "montant": autres_reserves + report_a_nouveau},
            {"year": yr, "mass": "I. FINANCEMENT PERMANENT", "rubrique": "  - Résultat net de l'exercice", "montant": resultat_net},
            {"year": yr, "mass": "I. FINANCEMENT PERMANENT", "rubrique": "Capitaux propres assimilés", "montant": capitaux_assimiles},
            {"year": yr, "mass": "I. FINANCEMENT PERMANENT", "rubrique": "Dettes de financement", "montant": dettes_financement},
            {"year": yr, "mass": "I. FINANCEMENT PERMANENT", "rubrique": "Provisions durables pour risques & charges", "montant": provisions_durables},
            {"year": yr, "mass": "I. FINANCEMENT PERMANENT", "rubrique": "TOTAL I - FINANCEMENT PERMANENT", "montant": total_financement_permanent},

            {"year": yr, "mass": "II. PASSIF CIRCULANT (HT)", "rubrique": "Dettes du passif circulant", "montant": dettes_passif_circ},
            {"year": yr, "mass": "II. PASSIF CIRCULANT (HT)", "rubrique": "Autres prov. risques & charges circ.", "montant": autres_prov_risques},
            {"year": yr, "mass": "II. PASSIF CIRCULANT (HT)", "rubrique": "TOTAL II - PASSIF CIRCULANT HT", "montant": total_passif_circulant},

            {"year": yr, "mass": "III. TRESORERIE PASSIF", "rubrique": "Crédits de trésorerie & escompte", "montant": credits_escompte + credits_tresorerie},
            {"year": yr, "mass": "III. TRESORERIE PASSIF", "rubrique": "Banques (soldes créditeurs)", "montant": banques_solde_crediteur},
            {"year": yr, "mass": "III. TRESORERIE PASSIF", "rubrique": "TOTAL III - TRESORERIE PASSIF", "montant": total_tresorerie_passif},

            {"year": yr, "mass": "TOTAL GENERAL PASSIF", "rubrique": "TOTAL GENERAL PASSIF (I + II + III)", "montant": total_general_passif},
        ])

    return pd.DataFrame(actif_rows), pd.DataFrame(passif_rows)
