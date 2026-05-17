"""
regression_ml.py
================
Regression on an unknown dataset (dataset.csv) using multiple scikit-learn
algorithms to predict the continuous target variable COL_134.

Algorithms applied
------------------
1. Linear Regression          - Baseline linear model
2. Ridge Regression           - L2-regularised linear model
3. Lasso Regression           - L1-regularised, sparse feature selection
4. Random Forest Regressor    - Ensemble tree-based model
5. Gradient Boosting          - Sequential boosting (scikit-learn)
6. XGBoost Regressor          - Extreme gradient boosting
7. LightGBM Regressor         - Fast histogram-based boosting
8. Support Vector Regression  - Kernel-based regression (SVR)

Usage (inside virtual environment)
-----------------------------------
    python regression_ml.py

Output
------
  plots/regression_model_comparison.png   Bar chart: model R² scores
  plots/regression_predictions.png        Scatter: actual vs predicted (best model)
  plots/regression_residuals.png          Residual distribution (best model)
"""

import os
import warnings
import time

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — safe for all environments
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error,
    root_mean_squared_error,
)

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# 0. Configuration
# ---------------------------------------------------------------------------
DATASET_PATH = "dataset.csv"
TARGET_COL   = "COL_134"     # last column — continuous property to predict
ID_COL       = "ID"          # identifier column — drop before training
RANDOM_STATE = 42
TEST_SIZE    = 0.20
PLOTS_DIR    = "plots"

os.makedirs(PLOTS_DIR, exist_ok=True)

print("=" * 70)
print("  Regression on unknown dataset  —  target:", TARGET_COL)
print("=" * 70)

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
print("\n[1] Loading dataset …")
df = pd.read_csv(DATASET_PATH, sep=";", low_memory=False)
print(f"    Raw shape : {df.shape[0]:,} rows × {df.shape[1]} columns")

# ---------------------------------------------------------------------------
# 2. Basic pre-processing
# ---------------------------------------------------------------------------
print("\n[2] Pre-processing …")

# Drop the identifier column — it carries no predictive signal
if ID_COL in df.columns:
    df.drop(columns=[ID_COL], inplace=True)

# Separate target
y = pd.to_numeric(df[TARGET_COL], errors="coerce")
X_raw = df.drop(columns=[TARGET_COL])

# Keep only numeric-castable columns
X_numeric = X_raw.apply(pd.to_numeric, errors="coerce")

# Drop columns that are entirely NaN (all values non-numeric / completely empty)
X_numeric.dropna(axis=1, how="all", inplace=True)

# Replace infinity values with NaN so the imputer can handle them
X_numeric.replace([np.inf, -np.inf], np.nan, inplace=True)

# Drop rows where target is NaN
valid_idx = y.notna()
X_numeric = X_numeric[valid_idx]
y = y[valid_idx]

print(f"    Numeric features retained : {X_numeric.shape[1]}")
print(f"    Training samples          : {len(y):,}")
print(f"    Target range              : [{y.min():.4f}, {y.max():.4f}]")
print(f"    Target mean ± std         : {y.mean():.4f} ± {y.std():.4f}")

# ---------------------------------------------------------------------------
# 3. Train / test split  (always split BEFORE any feature selection or scaling)
# ---------------------------------------------------------------------------
print("\n[3] Splitting dataset …")
X_train, X_test, y_train, y_test = train_test_split(
    X_numeric, y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
)
print(f"    Train : {len(y_train):,}  |  Test : {len(y_test):,}")

# ---------------------------------------------------------------------------
# 4. Build pre-processing + model pipelines
# ---------------------------------------------------------------------------
# Pre-processing steps shared by all linear / SVR models:
#   (a) median imputation for missing values
#   (b) standard scaling  (zero mean, unit variance)
#
# Tree-based models (RF, GB, XGB, LGBM) tolerate NaN natively after imputation
# but do not require scaling.

def make_linear_pipeline(estimator):
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("model",   estimator),
    ])

def make_tree_pipeline(estimator):
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model",   estimator),
    ])

models = {
    "Linear Regression":       make_linear_pipeline(LinearRegression()),
    "Ridge Regression":        make_linear_pipeline(Ridge(alpha=1.0, random_state=RANDOM_STATE)),
    "Lasso Regression":        make_linear_pipeline(Lasso(alpha=0.001, max_iter=5000, random_state=RANDOM_STATE)),
    "Random Forest":           make_tree_pipeline(RandomForestRegressor(n_estimators=200, n_jobs=-1, random_state=RANDOM_STATE)),
    "Gradient Boosting":       make_tree_pipeline(GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, random_state=RANDOM_STATE)),
    "XGBoost":                 make_tree_pipeline(XGBRegressor(n_estimators=200, learning_rate=0.05, n_jobs=-1, verbosity=0, random_state=RANDOM_STATE)),
    "LightGBM":                make_tree_pipeline(LGBMRegressor(n_estimators=200, learning_rate=0.05, n_jobs=-1, verbose=-1, random_state=RANDOM_STATE)),
    "SVR (RBF kernel)":        make_linear_pipeline(SVR(kernel="rbf", C=1.0, epsilon=0.1)),
}

# ---------------------------------------------------------------------------
# 5. Train & evaluate all models
# ---------------------------------------------------------------------------
print("\n[4] Training and evaluating models …\n")
print(f"    {'Model':<28} {'R²':>8} {'MAE':>10} {'RMSE':>10}  {'Time(s)':>8}")
print("    " + "-" * 70)

results = {}
for name, pipeline in models.items():
    t0 = time.time()
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    elapsed = time.time() - t0

    r2   = r2_score(y_test, y_pred)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)

    results[name] = {
        "pipeline": pipeline,
        "y_pred":   y_pred,
        "R2":       r2,
        "MAE":      mae,
        "RMSE":     rmse,
        "time":     elapsed,
    }
    print(f"    {name:<28} {r2:>8.4f} {mae:>10.4f} {rmse:>10.4f}  {elapsed:>8.2f}s")

# ---------------------------------------------------------------------------
# 6. Identify best model by R²
# ---------------------------------------------------------------------------
best_name = max(results, key=lambda n: results[n]["R2"])
best      = results[best_name]
print(f"\n    Best model : {best_name}  (R² = {best['R2']:.4f})")

# ---------------------------------------------------------------------------
# 7. Cross-validation for best model (5-fold CV on training set)
# ---------------------------------------------------------------------------
print("\n[5] 5-fold cross-validation for best model …")
cv_scores = cross_val_score(
    best["pipeline"], X_train, y_train,
    cv=5, scoring="r2", n_jobs=-1,
)
print(f"    CV R² scores : {cv_scores}")
print(f"    Mean CV R²   : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ---------------------------------------------------------------------------
# 8. Plots
# ---------------------------------------------------------------------------
print("\n[6] Generating plots …")

sns.set_theme(style="whitegrid", palette="muted")

# --- Plot 1: Model comparison bar chart (R² scores) ---
fig, ax = plt.subplots(figsize=(12, 6))
names  = list(results.keys())
r2vals = [results[n]["R2"] for n in names]
colors = ["#2ecc71" if n == best_name else "#3498db" for n in names]

bars = ax.barh(names, r2vals, color=colors, edgecolor="white", height=0.6)
ax.bar_label(bars, labels=[f"{v:.4f}" for v in r2vals], padding=4, fontsize=9)
ax.set_xlabel("R² Score (higher = better)")
ax.set_title("Regression Model Comparison — R² on Hold-out Test Set", fontsize=13, fontweight="bold")
ax.axvline(0, color="grey", linewidth=0.8, linestyle="--")
ax.set_xlim(min(min(r2vals) - 0.05, -0.05), max(r2vals) + 0.10)
ax.invert_yaxis()

# Annotate best model
ax.annotate(
    "← Best model",
    xy=(best["R2"], names.index(best_name)),
    xytext=(best["R2"] + 0.03, names.index(best_name) - 0.35),
    fontsize=8, color="#27ae60",
    arrowprops=dict(arrowstyle="->", color="#27ae60"),
)

plt.tight_layout()
path1 = os.path.join(PLOTS_DIR, "regression_model_comparison.png")
plt.savefig(path1, dpi=150)
plt.close()
print(f"    Saved → {path1}")

# --- Plot 2: Actual vs Predicted scatter (best model) ---
fig, ax = plt.subplots(figsize=(7, 7))
y_pred_best = best["y_pred"]

ax.scatter(y_test, y_pred_best, alpha=0.35, s=18, color="#3498db", edgecolors="none", label="Samples")
lims = [min(y_test.min(), y_pred_best.min()) - 0.02,
        max(y_test.max(), y_pred_best.max()) + 0.02]
ax.plot(lims, lims, "r--", linewidth=1.5, label="Perfect prediction")
ax.set_xlabel("Actual (COL_134)")
ax.set_ylabel("Predicted (COL_134)")
ax.set_title(f"Actual vs Predicted — {best_name}\nR² = {best['R2']:.4f}  |  RMSE = {best['RMSE']:.4f}  |  MAE = {best['MAE']:.4f}",
             fontsize=11, fontweight="bold")
ax.legend()
plt.tight_layout()
path2 = os.path.join(PLOTS_DIR, "regression_predictions.png")
plt.savefig(path2, dpi=150)
plt.close()
print(f"    Saved → {path2}")

# --- Plot 3: Residual distribution (best model) ---
residuals = y_test.values - y_pred_best
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].scatter(y_pred_best, residuals, alpha=0.3, s=15, color="#e67e22", edgecolors="none")
axes[0].axhline(0, color="red", linewidth=1.2, linestyle="--")
axes[0].set_xlabel("Predicted values")
axes[0].set_ylabel("Residuals (Actual − Predicted)")
axes[0].set_title("Residuals vs Fitted")

axes[1].hist(residuals, bins=60, color="#9b59b6", edgecolor="white", alpha=0.85)
axes[1].axvline(0, color="red", linewidth=1.5, linestyle="--")
axes[1].set_xlabel("Residual value")
axes[1].set_ylabel("Frequency")
axes[1].set_title("Residual Distribution")

fig.suptitle(f"Residual Analysis — {best_name}", fontsize=13, fontweight="bold")
plt.tight_layout()
path3 = os.path.join(PLOTS_DIR, "regression_residuals.png")
plt.savefig(path3, dpi=150)
plt.close()
print(f"    Saved → {path3}")

# ---------------------------------------------------------------------------
# 9. Summary table
# ---------------------------------------------------------------------------
print("\n[7] Summary table\n")
summary = pd.DataFrame(
    {n: {"R²": r["R2"], "MAE": r["MAE"], "RMSE": r["RMSE"]} for n, r in results.items()}
).T.sort_values("R²", ascending=False)
print(summary.to_string(float_format=lambda x: f"{x:.4f}"))

print("\n" + "=" * 70)
print("  Done. All plots saved to:", PLOTS_DIR)
print("=" * 70)
