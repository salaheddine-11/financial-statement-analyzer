# Moroccan Financial Statement Analyzer

A Streamlit prototype that turns a Moroccan trial balance into standardized financial statements, using CGNC / Plan Comptable Marocain (PCM) logic.

## What it produces

- Standardized financial statements from a raw trial balance (`balance générale`)
- **Bilan comptable**
- **Bilan financier** — with *retraitements* and *reclassements*
- **CPC**
- **Soldes de gestion** — FRF, BFG and Trésorerie nette
- ESG indicators
- Financial ratios
- Red flags

## Repository layout

| Path | Contents |
|---|---|
| `app.py` | Streamlit entry point |
| `src/data_loader.py` | Reads CSV / Excel trial balances |
| `src/validation.py` | Validates balance and column structure |
| `src/pcge_mapper.py` | Maps PCM accounts using `config/pcge_mapping.yaml` |
| `src/bilan.py` | Bilan comptable |
| `src/retraitements.py` | Bilan financier (retraitements + reclassements) |
| `src/cpc.py` | Compte de produits et charges |
| `src/esg.py` | ESG indicators |
| `src/financial_analysis.py` | Ratios and red flags |
| `data/` | Sample trial balance (CSV + XLSX) |
| `tests/` | End-to-end tests over the sample data |
| `notes/` | Reference material |

## Run the app

Requires Python 3 — `requirements.txt` pins the versions the project was built with.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

With [uv](https://docs.astral.sh/uv/):

```bash
uv run --with-requirements requirements.txt streamlit run app.py
```

The app opens at http://localhost:8501. Upload `data/sample_trial_balance.csv` to try it end to end.

## Tests

```bash
pip install pytest
pytest
```

## Accounting basis

Moroccan statutory financial statements are generally prepared at historical cost. Book values may therefore differ from economic values; the *bilan financier* and its *retraitements* exist precisely to bridge that gap.

## Disclaimer

Prototype for educational purposes only. It does not replace professional judgment, audit work, or financial advisory.
