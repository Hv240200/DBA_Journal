# Knowledge-Based AI and Data-Driven Decision Support

Compact, fully reproducible experiments supporting a Short Communication on
knowledge-guided quality triage for manufacturing digital transformation.

## Data and reproducibility

The code downloads the original [UCI Steel Plates Faults dataset](https://archive.ics.uci.edu/dataset/198/steel%2Bplates%2Bfaults)
(Buscema, Terzi, and Tastle, 2010; DOI: 10.24432/C5J88N; CC BY 4.0). The source
contains 1,941 labeled examples, 27 features, and seven fault classes.
The source ZIP is not stored in this repository. The script records its SHA-256.

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python research.py --output results
```

Offline, if you previously downloaded the original UCI ZIP:

```powershell
python research.py --data steel_plates_source.zip --output results
```

The one-command run generates `results/results.json`, `induced_rules.txt`, and
**exactly two figures**: an architecture diagram and a held-out risk--coverage
curve. The manuscript reports **exactly two tables** from these results.

## Experimental protocol

1. Fixed stratified 60/20/20 train/validation/test partition (seed 42).
2. Logistic regression and induced shallow-tree baseline; internally calibrated
   gradient boosting for primary multiclass prediction.
3. A transparent tree rule model, learned only from training observations,
   votes on whether to trust each gradient-boosted predicted class. The analysis
   also audits conditional error and confidence for agreement/disagreement cases.
4. The knowledge-guided confidence score is `p_max` if the tree agrees and
   `0.65 * p_max` otherwise; the penalty is fixed before test evaluation.
5. A **validation-only evidence gate** chooses the candidate policy with lower
   error at the fixed 80%-coverage target; it defaults to confidence-only on ties.
   Its choice is frozen before test evaluation, so a weak symbolic candidate
   is not automatically deployed.
6. Compare confidence-only and knowledge-guided selective risks at matched
   retrospective review budgets (60%, 80%, 90% automated coverage), with paired
   bootstrap 95% uncertainty intervals at 80% coverage.
7. Separately report a deployable threshold selected using **validation data
   only**; held-out rankings are for retrospective risk--coverage analysis.

## Interpretation and limits

- These are **data-induced symbolic rules**, not verified SOPs or expert-coded
  process knowledge. The system decides whether to auto-handle a predicted label
  or request human review; it does not recommend repairs or maintenance actions.
- Neither inspection costs nor factory intervention results exist in this UCI
  dataset. Accuracy/selective risk are measured; factory savings are not.
- The title's digital transformation, innovation, and entrepreneurship themes
  describe potential applications, **not measured entrepreneurial outcomes**.
- A real factory deployment would require expert review, temporal/external
  validation, approved quality SOPs, and a pre-specified human-review policy.

## Minimal structure

`research.py` is the complete executable experiment, `requirements.txt` pins
compatible dependency ranges, and this README documents its scope. Generated
figures/results are intentionally not tracked.
