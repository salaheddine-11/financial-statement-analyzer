import os

import pandas as pd
import streamlit as st

from src.data_loader import load_trial_balance
from src.validation import validate_trial_balance
from src.pcge_mapper import (
    load_mapping_rules,
    mapping_rules_to_dataframe,
    preview_account_coverage,
    map_trial_balance,
    get_unmapped_accounts,
    summarize_mapped_amounts,
)
from src.bilan import compute_bilan_comptable
from src.cpc import compute_cpc
from src.esg import compute_esg
from src.financial_analysis import compute_financial_analysis
from src.retraitements import compute_bilan_financier

st.set_page_config(
    page_title="Moroccan Financial Statement Analyzer (PCGM / CGNC)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich aesthetics
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-header">🇲🇦 Moroccan Financial Statement Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Statutory Financial Analysis System strictly aligned with CGNC & PCGM (Plan Comptable Général Marocain)</div>', unsafe_allow_html=True)

st.info(
    "💡 **Accounting Standard Notice**: Moroccan statutory financial statements are prepared under historical cost principles "
    "according to Code Général de la Normalisation Comptable (CGNC). Amounts are expressed in Moroccan Dirham (MAD)."
)

# Sidebar File Uploader
st.sidebar.header("📁 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload Trial Balance (CSV)", type=["csv"])

trial_balance = None
source_name = None

if uploaded_file is not None:
    trial_balance = load_trial_balance(uploaded_file)
    source_name = uploaded_file.name
elif os.path.exists("data/sample_trial_balance.csv"):
    trial_balance = load_trial_balance("data/sample_trial_balance.csv")
    source_name = "data/sample_trial_balance.csv (PCGM Sample)"

rules = None
rules_error = None

try:
    rules = load_mapping_rules()
except FileNotFoundError:
    rules_error = "Configuration file not found: config/pcge_mapping.yaml"
except Exception as exception:
    rules_error = str(exception)

mapped_trial_balance = None
unmapped_accounts = None
mapped_summary = None

if trial_balance is not None and rules is not None:
    mapped_trial_balance = map_trial_balance(trial_balance, rules)
    unmapped_accounts = get_unmapped_accounts(mapped_trial_balance)
    mapped_summary = summarize_mapped_amounts(mapped_trial_balance)

# Main Navigation Tabs
tab_tb, tab_mapping, tab_bilan, tab_cpc, tab_esg, tab_analysis = st.tabs(
    [
        "📋 Balance de Vérification",
        "⚙️ Mapping PCGM",
        "🏛️ Bilan Comptable",
        "📈 CPC (Produits & Charges)",
        "📊 ESG & CAF",
        "🎯 Analyse Financière & Ratios",
    ]
)

# -------------------------------------------------------------------
# TAB 1: TRIAL BALANCE
# -------------------------------------------------------------------
with tab_tb:
    st.subheader("Balance de Vérification — Trial Balance Loading & Verification")

    if trial_balance is None:
        st.warning("No trial balance found. Please upload a CSV file.")
    else:
        st.success(f"Loaded: `{source_name}`")

        validation = validate_trial_balance(trial_balance)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(trial_balance))
        with col2:
            st.metric("Years Analyzed", ", ".join(map(str, sorted(trial_balance["year"].unique()))))
        with col3:
            is_balanced = validation["balanced"].all()
            st.metric("Trial Balance Status", "BALANCED ✅" if is_balanced else "UNBALANCED ❌")

        st.subheader("Balance Validation by Year")
        st.dataframe(validation, use_container_width=True)

        st.subheader("Raw Trial Balance Accounts")
        st.dataframe(trial_balance, use_container_width=True)

# -------------------------------------------------------------------
# TAB 2: MAPPING PCGM
# -------------------------------------------------------------------
with tab_mapping:
    st.subheader("PCGM Chart of Accounts Mapping")

    if rules_error is not None:
        st.error(rules_error)
    else:
        rules_df = mapping_rules_to_dataframe(rules)
        st.subheader("PCGM Mapping Rules Configuration")
        st.dataframe(rules_df, use_container_width=True)

        if trial_balance is not None:
            coverage = preview_account_coverage(trial_balance, rules)

            st.subheader("Trial Balance Account Coverage Preview")
            st.dataframe(coverage, use_container_width=True)

            unmapped_cov = coverage[coverage["mapped"] == False]
            if unmapped_cov.empty:
                st.success("✅ All accounts in trial balance are mapped to PCGM classes.")
            else:
                st.error(f"⚠️ {len(unmapped_cov)} accounts are unmapped!")
                st.dataframe(unmapped_cov, use_container_width=True)

# -------------------------------------------------------------------
# TAB 3: BILAN COMPTABLE
# -------------------------------------------------------------------
with tab_bilan:
    st.subheader("Bilan Comptable (Moroccan Statutory Balance Sheet)")

    if mapped_trial_balance is None:
        st.info("Please load a valid trial balance.")
    else:
        df_actif, df_passif = compute_bilan_comptable(mapped_trial_balance)
        selected_year = st.selectbox("Select Year", sorted(mapped_trial_balance["year"].unique()), key="bilan_year")

        act_yr = df_actif[df_actif["year"] == selected_year]
        pas_yr = df_passif[df_passif["year"] == selected_year]

        col_a, col_p = st.columns(2)

        with col_a:
            st.markdown("### 🔹 ACTIF")
            st.dataframe(
                act_yr[["mass", "rubrique", "brut", "amort_prov", "net"]].style.format(
                    {"brut": "{:,.2f} MAD", "amort_prov": "{:,.2f} MAD", "net": "{:,.2f} MAD"}
                ),
                use_container_width=True,
                height=500,
            )

        with col_p:
            st.markdown("### 🔸 PASSIF")
            st.dataframe(
                pas_yr[["mass", "rubrique", "montant"]].style.format(
                    {"montant": "{:,.2f} MAD"}
                ),
                use_container_width=True,
                height=500,
            )

# -------------------------------------------------------------------
# TAB 4: CPC
# -------------------------------------------------------------------
with tab_cpc:
    st.subheader("Compte de Produits et Charges (CPC)")

    if mapped_trial_balance is None:
        st.info("Please load a valid trial balance.")
    else:
        df_cpc = compute_cpc(mapped_trial_balance)
        selected_year_cpc = st.selectbox("Select Year", sorted(mapped_trial_balance["year"].unique()), key="cpc_year")

        cpc_yr = df_cpc[df_cpc["year"] == selected_year_cpc]

        st.dataframe(
            cpc_yr[["section", "rubrique", "montant"]].style.format(
                {"montant": "{:,.2f} MAD"}
            ),
            use_container_width=True,
            height=600,
        )

# -------------------------------------------------------------------
# TAB 5: ESG & CAF
# -------------------------------------------------------------------
with tab_esg:
    st.subheader("État des Soldes de Gestion (ESG) & Capacité d'Autofinancement (CAF)")

    if mapped_trial_balance is None:
        st.info("Please load a valid trial balance.")
    else:
        df_tfr, df_caf = compute_esg(mapped_trial_balance)
        selected_year_esg = st.selectbox("Select Year", sorted(mapped_trial_balance["year"].unique()), key="esg_year")

        tfr_yr = df_tfr[df_tfr["year"] == selected_year_esg]
        caf_yr = df_caf[df_caf["year"] == selected_year_esg]

        st.markdown("### 1️⃣ Tableau de Formation du Résultat (TFR)")
        st.dataframe(
            tfr_yr[["indicateur", "valeur"]].style.format({"valeur": "{:,.2f} MAD"}),
            use_container_width=True,
        )

        st.markdown("### 2️⃣ Capacité d'Autofinancement (CAF)")
        st.dataframe(
            caf_yr[["element", "montant"]].style.format({"montant": "{:,.2f} MAD"}),
            use_container_width=True,
        )

# -------------------------------------------------------------------
# TAB 6: FINANCIAL ANALYSIS & RATIOS
# -------------------------------------------------------------------
with tab_analysis:
    st.subheader("Indicateurs d'Équilibre Financier, Bilan Financier & Ratios")

    if mapped_trial_balance is None:
        st.info("Please load a valid trial balance.")
    else:
        df_eq, df_ratios = compute_financial_analysis(mapped_trial_balance)
        df_bf = compute_bilan_financier(mapped_trial_balance)

        selected_year_an = st.selectbox("Select Year", sorted(mapped_trial_balance["year"].unique()), key="an_year")

        eq_yr = df_eq[df_eq["year"] == selected_year_an]
        ratios_yr = df_ratios[df_ratios["year"] == selected_year_an]
        bf_yr = df_bf[df_bf["year"] == selected_year_an]

        # Key Equilibrium KPI Cards
        frf_val = eq_yr[eq_yr["indicator"] == "1. FONDS DE ROULEMENT FONCTIONNEL (FRF)"]["value"].values[0]
        bfr_val = eq_yr[eq_yr["indicator"] == "2. BESOIN EN FONDS DE ROULEMENT (BFR)"]["value"].values[0]
        tn_val = eq_yr[eq_yr["indicator"] == "3. TRESORERIE NETTE (TN = FRF - BFR)"]["value"].values[0]

        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("FRF (Financement Permanent - Actif Immob)", f"{frf_val:,.2f} MAD")
        with kpi2:
            st.metric("BFR (Actif Circulant HT - Passif Circulant HT)", f"{bfr_val:,.2f} MAD")
        with kpi3:
            st.metric("TN (Trésorerie Nette = FRF - BFR)", f"{tn_val:,.2f} MAD", delta="Equilibrium OK" if tn_val >= 0 else "Cash Deficit")

        st.markdown("### ⚖️ Indicateurs d'Équilibre Financier")
        st.dataframe(
            eq_yr[["indicator", "value"]].style.format({"value": "{:,.2f} MAD"}),
            use_container_width=True,
        )

        st.markdown("### 🔄 Bilan Financier (Retraitement des Non-Valeurs)")
        st.dataframe(
            bf_yr[["rubrique", "comptable", "retraitement", "financier"]].style.format(
                {"comptable": "{:,.2f} MAD", "retraitement": "{:,.2f} MAD", "financier": "{:,.2f} MAD"}
            ),
            use_container_width=True,
        )

        st.markdown("### 📐 Ratios Financiers Marocains & Diagnostics")
        st.dataframe(
            ratios_yr[["category", "ratio_name", "value", "unit", "norm"]].style.format(
                {"value": "{:,.2%}"}
            ),
            use_container_width=True,
        )