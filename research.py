"""Reproducible knowledge-guided quality triage on the UCI Steel Plates Faults data.

Run: python research.py --output results
The rule model is learned from training data; it is NOT an expert-validated SOP.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import urllib.request
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text


SOURCE = "https://archive.ics.uci.edu/static/public/198/steel+plates+faults.zip"
FAULTS = ("Pastry", "Z_Scratch", "K_Scatch", "Stains", "Dirtiness", "Bumps", "Other_Faults")
SEED = 42


def load_steel_data(path: str | None) -> tuple[np.ndarray, np.ndarray, list[str], str]:
    """Load the authoritative UCI archive without bundling or altering source data."""
    if path:
        raw = Path(path).read_bytes()
    else:
        with urllib.request.urlopen(SOURCE, timeout=45) as response:
            raw = response.read()
    digest = hashlib.sha256(raw).hexdigest()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        labels = archive.read("Faults27x7_var").decode("utf-8-sig").splitlines()
        matrix = pd.read_csv(io.BytesIO(archive.read("Faults.NNA")), sep=r"\s+", header=None)
    if matrix.shape != (1941, 34) or len(labels) != 34:
        raise ValueError(f"Unexpected UCI schema: rows/columns={matrix.shape}, labels={len(labels)}")
    onehot = matrix.iloc[:, 27:].to_numpy(dtype=int)
    if not np.all(onehot.sum(axis=1) == 1):
        raise ValueError("Each fault row must have exactly one positive class")
    if tuple(labels[27:]) != FAULTS:
        raise ValueError("Unexpected target class ordering")
    X = matrix.iloc[:, :27].to_numpy(dtype=np.float64)
    y = np.argmax(onehot, axis=1).astype(int)
    if not np.all(np.isfinite(X)):
        raise ValueError("Non-finite feature value in UCI data")
    return X, y, labels[:27], digest


def multiclass_brier(y: np.ndarray, proba: np.ndarray) -> float:
    truth = np.eye(proba.shape[1])[y]
    return float(np.mean(np.sum((proba - truth) ** 2, axis=1)))


def model_metrics(y: np.ndarray, proba: np.ndarray) -> dict[str, float]:
    pred = np.argmax(proba, axis=1)
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "macro_f1": float(f1_score(y, pred, average="macro", zero_division=0)),
        "brier": multiclass_brier(y, proba),
        "log_loss": float(log_loss(y, proba, labels=np.arange(7))),
    }


def select_at_coverage(score: np.ndarray, fraction: float) -> np.ndarray:
    """Rank-only retrospective analysis; never use test ranks as deployment thresholds."""
    if not 0 < fraction <= 1:
        raise ValueError("Coverage must be in (0, 1]")
    k = max(1, math.floor(len(score) * fraction))
    chosen = np.argsort(-score, kind="stable")[:k]
    result = np.zeros(len(score), dtype=bool)
    result[chosen] = True
    assert result.sum() == k
    return result


def selective_error(y: np.ndarray, pred: np.ndarray, score: np.ndarray, coverage: float) -> float:
    selected = select_at_coverage(score, coverage)
    return float(np.mean(pred[selected] != y[selected]))


def paired_bootstrap(
    y: np.ndarray,
    pred: np.ndarray,
    baseline_score: np.ndarray,
    hybrid_score: np.ndarray,
    coverage: float,
    *,
    repetitions: int = 2000,
    seed: int = SEED,
) -> tuple[float, float]:
    """Percentile CI for (hybrid risk - confidence-only risk)."""
    rng = np.random.default_rng(seed)
    values = np.empty(repetitions)
    for i in range(repetitions):
        ids = rng.integers(0, len(y), len(y))
        values[i] = selective_error(y[ids], pred[ids], hybrid_score[ids], coverage) - selective_error(
            y[ids], pred[ids], baseline_score[ids], coverage
        )
    return tuple(float(x) for x in np.quantile(values, [0.025, 0.975]))


def plot_architecture(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 3.55))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 3.8)
    ax.axis("off")

    boxes = [
        (0.2, 0.85, 2.5, 1.3, "Steel plate\nmeasurements", "#E7EFF8"),
        (3.35, 1.72, 2.7, 0.86, "Calibrated ML\nprobabilities", "#DCECE8"),
        (3.35, 0.33, 2.7, 0.86, "Train-derived\ndecision rules", "#FFF0DB"),
        (6.75, 0.83, 2.8, 1.37, "Candidate scores:\nconfidence / agreement", "#E4E6FA"),
        (10.15, 0.83, 2.55, 1.37, "Automated label\nor human review", "#E8F0EA"),
    ]
    for x, y, w, h, label, fc in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12", fc=fc, ec="#41536A", lw=1.1))
        ax.text(x+w/2, y+h/2, label, ha="center", va="center", fontsize=10, weight="medium", color="#243444")
    arrows = [((2.8, 1.65), (3.25, 2.1)), ((2.8, 1.35), (3.25, 0.74)),
              ((6.12, 2.1), (6.65, 1.55)), ((6.12, 0.75), (6.65, 1.21)),
              ((9.68, 1.51), (10.06, 1.51))]
    for a, b in arrows:
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=13, lw=1.15, color="#52647C"))
    ax.add_patch(FancyBboxPatch((6.72, 2.67), 5.98, 0.67, boxstyle="round,pad=0.06,rounding_size=0.10",
                               fc="#F6F8FA", ec="#8C9BA8", lw=0.9, linestyle="--"))
    ax.text(9.71, 3.0, "Validation audit: compare risk at equal coverage; deploy lower-risk policy",
            ha="center", va="center", fontsize=9.0, color="#243444")
    ax.add_patch(FancyArrowPatch((8.13, 2.21), (8.13, 2.58), arrowstyle="-|>",
                                 mutation_scale=12, lw=1.1, color="#52647C"))
    ax.add_patch(FancyArrowPatch((11.5, 2.60), (11.5, 2.25), arrowstyle="-|>",
                                 mutation_scale=12, lw=1.1, color="#52647C"))
    fig.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_risk_coverage(path: Path, y: np.ndarray, pred: np.ndarray, scores: dict[str, np.ndarray]) -> None:
    coverage = np.linspace(0.40, 1.0, 61)
    fig, ax = plt.subplots(figsize=(7.3, 4.05))
    palette = {"Confidence only": "#1D5887", "Knowledge guided": "#B05B28"}
    for key, score in scores.items():
        risk = [selective_error(y, pred, score, float(c)) for c in coverage]
        ax.plot(100*coverage, 100*np.array(risk), label=key, lw=2.35, color=palette[key])
        at_80 = selective_error(y, pred, score, 0.80)
        ax.scatter([80], [100*at_80], color=palette[key], s=46, zorder=4)
    ax.set_xlabel("Automatically handled cases (%)", fontsize=10.5)
    ax.set_ylabel("Incorrect classifications among handled cases (%)", fontsize=10.5)
    ax.set_title("Selective risk at matched review budgets", fontsize=12, pad=12)
    ax.grid(alpha=0.2, linewidth=0.65)
    ax.legend(frameon=False, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def evaluate(input_zip: str | None, output: Path, seed: int, bootstraps: int) -> dict:
    X, y, feature_names, digest = load_steel_data(input_zip)
    idx = np.arange(len(y))
    trainval, test = train_test_split(idx, test_size=0.20, stratify=y, random_state=seed)
    train, valid = train_test_split(trainval, test_size=0.25, stratify=y[trainval], random_state=seed)
    assert len(set(train) & set(valid)) == len(set(train) & set(test)) == len(set(valid) & set(test)) == 0

    logistic = make_pipeline(StandardScaler(), LogisticRegression(max_iter=4000, class_weight="balanced"))
    logistic.fit(X[train], y[train])
    rules = DecisionTreeClassifier(max_depth=4, min_samples_leaf=30, random_state=seed)
    rules.fit(X[train], y[train])
    # Sigmoid calibration is internal to training; validation/test labels are untouched.
    learner = CalibratedClassifierCV(
        HistGradientBoostingClassifier(max_iter=180, learning_rate=0.07, max_leaf_nodes=15,
                                       min_samples_leaf=20, l2_regularization=0.25, random_state=seed),
        method="sigmoid", cv=3,
    )
    learner.fit(X[train], y[train])

    y_test = y[test]
    test_prob = learner.predict_proba(X[test])
    test_pred = np.argmax(test_prob, axis=1)
    rule_pred = rules.predict(X[test])
    agreement = rule_pred == test_pred
    baseline_score = test_prob.max(axis=1)
    # Fixed, disclosed consistency penalty - not fitted to test labels.
    hybrid_score = baseline_score * np.where(agreement, 1.0, 0.65)

    valid_prob = learner.predict_proba(X[valid])
    valid_ml_class = np.argmax(valid_prob, axis=1)
    valid_base = valid_prob.max(axis=1)
    valid_hybrid = valid_base * np.where(valid_ml_class == rules.predict(X[valid]), 1.0, 0.65)
    validation_risk = {
        "Confidence only": selective_error(y[valid], valid_ml_class, valid_base, 0.80),
        "Knowledge guided": selective_error(y[valid], valid_ml_class, valid_hybrid, 0.80),
    }
    # Evidence gate: knowledge influences deployment only when validation shows
    # a strictly lower selective error at the predeclared 80%-coverage target.
    gated_choice = "Knowledge guided" if validation_risk["Knowledge guided"] < validation_risk["Confidence only"] else "Confidence only"
    operating = {}
    for name, score_valid, score_test in (("Confidence only", valid_base, baseline_score),
                                          ("Knowledge guided", valid_hybrid, hybrid_score)):
        # Calibrate the deployment cut-off on validation only, never on held-out labels.
        cut = float(np.quantile(score_valid, 0.20))
        accepted = score_test >= cut
        operating[name] = {
            "validation_cutoff_for_80pct_target": cut,
            "heldout_coverage": float(accepted.mean()),
            "heldout_selective_error": float(np.mean(test_pred[accepted] != y_test[accepted]))
                if accepted.any() else None,
        }

    scores = {"Confidence only": baseline_score, "Knowledge guided": hybrid_score}
    selective = {}
    for fraction in (0.60, 0.80, 0.90):
        selective[str(fraction)] = {
            name: {"error": selective_error(y_test, test_pred, score, fraction),
                   "accepted": int(select_at_coverage(score, fraction).sum())}
            for name, score in scores.items()
        }

    diffs_ci = paired_bootstrap(y_test, test_pred, baseline_score, hybrid_score, 0.80,
                                repetitions=bootstraps, seed=seed)
    ml_metrics = model_metrics(y_test, test_prob)
    baseline_models = {
        "Logistic regression": model_metrics(y_test, logistic.predict_proba(X[test])),
        "Induced rules (tree)": model_metrics(y_test, rules.predict_proba(X[test])),
        "Calibrated gradient boosting": ml_metrics,
    }
    audit = {}
    for name, subset in (("agree", agreement), ("disagree", ~agreement)):
        audit[name] = {
            "n": int(subset.sum()),
            "error_rate": float(np.mean(test_pred[subset] != y_test[subset])),
            "mean_ml_confidence": float(baseline_score[subset].mean()),
        }
    gated_test_80 = selective_error(y_test, test_pred, scores[gated_choice], 0.80)
    output.mkdir(parents=True, exist_ok=True)
    plot_architecture(output / "figure_1_architecture.png")
    plot_risk_coverage(output / "figure_2_risk_coverage.png", y_test, test_pred, scores)
    (output / "induced_rules.txt").write_text(export_text(rules, feature_names=feature_names, max_depth=4), encoding="utf-8")
    result = {
        "source": SOURCE, "dataset_sha256": digest, "seed": seed,
        "n": len(y), "train_n": len(train), "valid_n": len(valid), "test_n": len(test),
        "class_support": {FAULTS[c]: int(np.sum(y == c)) for c in range(7)},
        "model_metrics": baseline_models,
        "rule_agreement_heldout": float(agreement.mean()),
        "agreement_audit_heldout": audit,
        "validation_evidence_gate": {
            "validation_selective_error_at_80pct": validation_risk,
            "selected_policy": gated_choice,
            "heldout_selective_error_at_80pct": gated_test_80,
        },
        "retrospective_equal_coverage": selective,
        "paired_bootstrap_delta_hybrid_minus_baseline_at_80pct": {
            "point": selective["0.8"]["Knowledge guided"]["error"] - selective["0.8"]["Confidence only"]["error"],
            "ci95_lower": diffs_ci[0], "ci95_upper": diffs_ci[1], "n_resamples": bootstraps,
        },
        "validation_threshold_operating_point": operating,
        "limitations": [
            "Rule tree is data-induced, not an expert-validated manufacturing SOP.",
            "Dataset provides labels, not action costs or intervention outcomes.",
            "Retrospective rank curves are diagnostic, not deployment thresholds.",
            "No SME adoption, entrepreneurship, or digital transformation outcomes are measured.",
        ],
    }
    (output / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", help="Optional local unmodified UCI ZIP; otherwise download from UCI")
    parser.add_argument("--output", type=Path, default=Path("results"))
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--bootstraps", type=int, default=2000)
    args = parser.parse_args()
    result = evaluate(args.data, args.output, args.seed, args.bootstraps)
    print(json.dumps({"metrics": result["model_metrics"], "selective": result["retrospective_equal_coverage"],
                      "bootstrap": result["paired_bootstrap_delta_hybrid_minus_baseline_at_80pct"]}, indent=2))


if __name__ == "__main__":
    main()
