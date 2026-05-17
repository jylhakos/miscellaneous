"""
feature_selection.py
====================
Applies multiple feature selection techniques to an unknown dataset
(dataset.csv) to identify the most predictive variables for the
continuous target variable COL_134.

Techniques demonstrated
-----------------------
1. Variance Threshold           — Remove near-zero variance features
2. Correlation Filter           — Pearson correlation with the target
3. Mutual Information           — Non-linear dependency measure (filter)
4. F-Regression                 — Univariate F-score with target (filter)
5. Random Forest Importances    — Embedded impurity-based importances
6. Lasso (L1) Embedded          — Embedded sparse coefficient selection
7. Recursive Feature Elimination (RFE) — Wrapper method via Ridge

Usage (inside virtual environment)
------------------------------------
    python feature_selection.py

Output
------
  plots/fs_correlation_heatmap.png      Heat map: top-20 feature correlations
  plots/fs_mutual_info.png              Bar chart: mutual information scores
  plots/fs_random_forest_importances.png Bar chart: Random Forest importances
  plots/fs_method_overlap.png           Venn / overlap bar: top-10 per method
  plots/fs_lasso_path.png               Lasso coefficient shrinkage
"""

import os
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import (
    VarianceThreshold,
    SelectKBest,
    f_regression,
    mutual_info_regression,
    RFE,
    SelectFromModel,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# 0. Configuration
# ---------------------------------------------------------------------------
DATASET_PATH = "dataset.csv"
TARGET_COL   = "COL_134"
ID_COL       = "ID"
TOP_K        = 20      # features to display per method
RANDOM_STATE = 42
PLOTS_DIR    = "plots"

os.makedirs(PLOTS_DIR, exist_ok=True)

print("=" * 70)
print("  Feature Selection on unknown dataset  —  target:", TARGET_COL)
print("=" * 70)

# ---------------------------------------------------------------------------
# 1. Load & pre-process  (identical pre-processing to regression_ml.py)
# ---------------------------------------------------------------------------
print("\n[1] Loading and pre-processing …")
df = pd.read_csv(DATASET_PATH, sep=";", low_memory=False)

if ID_COL in df.columns:
    df.drop(columns=[ID_COL], inplace=True)

y = pd.to_numeric(df[TARGET_COL], errors="coerce")
X_raw = df.drop(columns=[TARGET_COL])

X_numeric = X_raw.apply(pd.to_numeric, errors="coerce")
X_numeric.dropna(axis=1, how="all", inplace=True)

# Replace infinity values with NaN so the imputer can handle them
X_numeric.replace([np.inf, -np.inf], np.nan, inplace=True)

valid_idx = y.notna()
X_numeric = X_numeric[valid_idx].reset_index(drop=True)
y = y[valid_idx].reset_index(drop=True)

feature_names = list(X_numeric.columns)
print(f"    Numeric features : {len(feature_names)}")
print(f"    Samples          : {len(y):,}")

# ---------------------------------------------------------------------------
# 2. Train / test split  — feature selection ONLY on train split
# ---------------------------------------------------------------------------
print("\n[2] Train/test split …")
X_train, X_test, y_train, y_test = train_test_split(
    X_numeric, y, test_size=0.20, random_state=RANDOM_STATE
)

# Impute training data for methods that cannot handle NaN
imputer = SimpleImputer(strategy="median")
X_train_imp = pd.DataFrame(
    imputer.fit_transform(X_train),
    columns=feature_names,
)
X_test_imp = pd.DataFrame(
    imputer.transform(X_test),
    columns=feature_names,
)

scaler = StandardScaler()
X_train_scaled = pd.DataFrame(
    scaler.fit_transform(X_train_imp),
    columns=feature_names,
)

print(f"    Train : {len(y_train):,}  |  Test : {len(y_test):,}")

# ---------------------------------------------------------------------------
# 3. Method 1 — Variance Threshold
# ---------------------------------------------------------------------------
print("\n[3] Variance Threshold …")
vt = VarianceThreshold(threshold=0.01)   # remove features with < 1 % variance
vt.fit(X_train_imp)
retained_var = [f for f, keep in zip(feature_names, vt.get_support()) if keep]
removed_var  = [f for f, keep in zip(feature_names, vt.get_support()) if not keep]
print(f"    Retained : {len(retained_var)}  |  Removed (low variance) : {len(removed_var)}")

# For downstream methods, work only with variance-retained features
X_train_vt = X_train_imp[retained_var]
X_train_sc_vt = X_train_scaled[retained_var]

# ---------------------------------------------------------------------------
# 4. Method 2 — Pearson Correlation Filter
# ---------------------------------------------------------------------------
print("\n[4] Pearson Correlation Filter …")
corr_series = (
    X_train_vt.assign(target=y_train.values)
    .corr()["target"]
    .drop("target")
    .abs()
    .sort_values(ascending=False)
)
top_corr = corr_series.head(TOP_K)
print(f"    Top 5 by |correlation|: {list(top_corr.index[:5])}")

# ---------------------------------------------------------------------------
# 5. Method 3 — Mutual Information (F-score for regression)
# ---------------------------------------------------------------------------
print("\n[5] Mutual Information …")
mi_scores = mutual_info_regression(
    X_train_vt, y_train, random_state=RANDOM_STATE
)
mi_series = pd.Series(mi_scores, index=retained_var).sort_values(ascending=False)
top_mi = mi_series.head(TOP_K)
print(f"    Top 5 by MI : {list(top_mi.index[:5])}")

# ---------------------------------------------------------------------------
# 6. Method 4 — F-Regression (Univariate ANOVA F-test)
# ---------------------------------------------------------------------------
print("\n[6] F-Regression …")
f_scores, f_pvals = f_regression(X_train_vt, y_train)
f_series  = pd.Series(f_scores, index=retained_var).sort_values(ascending=False)
top_f = f_series.head(TOP_K)
print(f"    Top 5 by F-score : {list(top_f.index[:5])}")

# ---------------------------------------------------------------------------
# 7. Method 5 — Random Forest Feature Importances (embedded)
# ---------------------------------------------------------------------------
print("\n[7] Random Forest Importances …")
rf = RandomForestRegressor(
    n_estimators=200, n_jobs=-1, random_state=RANDOM_STATE
)
rf.fit(X_train_vt, y_train)
rf_series = pd.Series(
    rf.feature_importances_, index=retained_var
).sort_values(ascending=False)
top_rf = rf_series.head(TOP_K)
print(f"    Top 5 by RF importance : {list(top_rf.index[:5])}")

# ---------------------------------------------------------------------------
# 8. Method 6 — Lasso (L1) Embedded Selection
# ---------------------------------------------------------------------------
print("\n[8] Lasso (L1) Embedded Selection …")
lasso = Lasso(alpha=0.001, max_iter=10000, random_state=RANDOM_STATE)
lasso.fit(X_train_sc_vt, y_train)
lasso_coef = pd.Series(
    np.abs(lasso.coef_), index=retained_var
).sort_values(ascending=False)
lasso_selected = lasso_coef[lasso_coef > 0].index.tolist()
top_lasso = lasso_coef.head(TOP_K)
print(f"    Features with non-zero coefficient : {len(lasso_selected)}")
print(f"    Top 5 Lasso coefficients : {list(top_lasso.index[:5])}")

# ---------------------------------------------------------------------------
# 9. Method 7 — Recursive Feature Elimination (RFE) with Ridge
# ---------------------------------------------------------------------------
print("\n[9] RFE with Ridge Regression (selecting top 20) …")
ridge_for_rfe = Ridge(alpha=1.0)
rfe = RFE(estimator=ridge_for_rfe, n_features_to_select=TOP_K, step=10)
rfe.fit(X_train_sc_vt, y_train)
rfe_selected = [f for f, s in zip(retained_var, rfe.support_) if s]
print(f"    RFE selected features : {rfe_selected[:5]} …")

# ---------------------------------------------------------------------------
# 10. Aggregate results — build a vote-based consensus ranking
# ---------------------------------------------------------------------------
print("\n[10] Aggregating rankings …")

all_methods = {
    "Correlation":       set(top_corr.index),
    "Mutual Info":       set(top_mi.index),
    "F-Regression":      set(top_f.index),
    "Random Forest":     set(top_rf.index),
    "Lasso":             set(top_lasso[top_lasso > 0].index),
    "RFE":               set(rfe_selected),
}

vote_counts = {}
for feat in retained_var:
    vote_counts[feat] = sum(feat in method_set for method_set in all_methods.values())

vote_series = pd.Series(vote_counts).sort_values(ascending=False)
consensus_top = vote_series[vote_series >= 2].index.tolist()
print(f"    Features selected by ≥ 2 methods : {len(consensus_top)}")
print(f"    Top consensus features            : {consensus_top[:10]}")

# ---------------------------------------------------------------------------
# 11. Plots
# ---------------------------------------------------------------------------
print("\n[11] Generating plots …")

sns.set_theme(style="whitegrid", palette="muted")

# --- Plot 1: Correlation heatmap (top-20 features + target) ---
top20_feat = top_corr.index.tolist()
corr_data  = X_train_vt[top20_feat].assign(**{TARGET_COL: y_train.values})
corr_matrix = corr_data.corr()

fig, ax = plt.subplots(figsize=(14, 12))
mask = np.zeros_like(corr_matrix, dtype=bool)
mask[np.triu_indices_from(mask)] = True
sns.heatmap(
    corr_matrix, mask=mask, cmap="coolwarm", center=0,
    annot=True, fmt=".2f", annot_kws={"size": 7},
    linewidths=0.4, ax=ax,
)
ax.set_title(
    f"Correlation Heat Map — Top {TOP_K} Features (by |Pearson r| with {TARGET_COL})",
    fontsize=11, fontweight="bold",
)
plt.tight_layout()
path1 = os.path.join(PLOTS_DIR, "fs_correlation_heatmap.png")
plt.savefig(path1, dpi=150)
plt.close()
print(f"    Saved → {path1}")

# --- Plot 2: Mutual information bar chart ---
fig, ax = plt.subplots(figsize=(10, 6))
top_mi_sorted = top_mi.sort_values()
colors_mi = ["#e74c3c" if f in set(top_rf.index[:10]) else "#3498db"
             for f in top_mi_sorted.index]
top_mi_sorted.plot(kind="barh", ax=ax, color=colors_mi, edgecolor="white")
ax.set_xlabel("Mutual Information Score")
ax.set_title(
    f"Top {TOP_K} Features — Mutual Information Regression\n"
    "(Red bars: also in top-10 Random Forest importances)",
    fontsize=11, fontweight="bold",
)
plt.tight_layout()
path2 = os.path.join(PLOTS_DIR, "fs_mutual_info.png")
plt.savefig(path2, dpi=150)
plt.close()
print(f"    Saved → {path2}")

# --- Plot 3: Random Forest feature importances ---
fig, ax = plt.subplots(figsize=(10, 6))
top_rf_sorted = top_rf.sort_values()
colors_rf = ["#e74c3c" if f in set(top_mi.index[:10]) else "#2ecc71"
             for f in top_rf_sorted.index]
top_rf_sorted.plot(kind="barh", ax=ax, color=colors_rf, edgecolor="white")
ax.set_xlabel("Mean Decrease in Impurity (Feature Importance)")
ax.set_title(
    f"Top {TOP_K} Features — Random Forest Importances\n"
    "(Red bars: also in top-10 Mutual Information)",
    fontsize=11, fontweight="bold",
)
plt.tight_layout()
path3 = os.path.join(PLOTS_DIR, "fs_random_forest_importances.png")
plt.savefig(path3, dpi=150)
plt.close()
print(f"    Saved → {path3}")

# --- Plot 4: Method overlap — votes per top feature ---
vote_top = vote_series.head(TOP_K).sort_values()
fig, ax = plt.subplots(figsize=(10, 6))
palette = {1: "#bdc3c7", 2: "#f39c12", 3: "#e67e22", 4: "#e74c3c",
           5: "#9b59b6", 6: "#2c3e50"}
bar_colors = [palette.get(int(v), "#95a5a6") for v in vote_top.values]
vote_top.plot(kind="barh", ax=ax, color=bar_colors, edgecolor="white")
ax.set_xlabel("Number of selection methods agreeing (max 6)")
ax.set_title(
    f"Feature Consensus — Top {TOP_K} Features Ranked by Method Agreement\n"
    "(Higher = selected by more methods)",
    fontsize=11, fontweight="bold",
)
ax.axvline(2, color="orange", linestyle="--", linewidth=1.2, label="≥ 2 methods threshold")
ax.legend(fontsize=9)
plt.tight_layout()
path4 = os.path.join(PLOTS_DIR, "fs_method_overlap.png")
plt.savefig(path4, dpi=150)
plt.close()
print(f"    Saved → {path4}")

# --- Plot 5: Lasso coefficient paths (vary alpha) ---
print("    Computing Lasso paths …")
alphas = np.logspace(-4, 1, 60)
coef_paths = []
for a in alphas:
    lm = Lasso(alpha=a, max_iter=10000, random_state=RANDOM_STATE)
    lm.fit(X_train_sc_vt, y_train)
    coef_paths.append(lm.coef_)
coef_array = np.array(coef_paths)           # shape: (n_alphas, n_features)

# Only plot top-10 features by max absolute coefficient across all alphas
max_abs = np.max(np.abs(coef_array), axis=0)
top10_idx = np.argsort(max_abs)[::-1][:10]

fig, ax = plt.subplots(figsize=(12, 6))
for idx in top10_idx:
    ax.plot(np.log10(alphas), coef_array[:, idx], linewidth=1.5,
            label=retained_var[idx])
ax.axvline(np.log10(0.001), color="red", linestyle="--", linewidth=1.2, label="Selected α=0.001")
ax.set_xlabel("log₁₀(α) — Regularisation Strength")
ax.set_ylabel("Coefficient value")
ax.set_title(
    "Lasso Regularisation Path — Top 10 Features\n"
    "(Coefficients shrink to zero as α increases — embedded feature elimination)",
    fontsize=11, fontweight="bold",
)
ax.legend(fontsize=8, loc="upper right", ncol=2)
plt.tight_layout()
path5 = os.path.join(PLOTS_DIR, "fs_lasso_path.png")
plt.savefig(path5, dpi=150)
plt.close()
print(f"    Saved → {path5}")

# ---------------------------------------------------------------------------
# 12. Print consensus feature table
# ---------------------------------------------------------------------------
print("\n[12] Consensus features (selected by ≥ 2 methods):\n")
header = f"    {'Feature':<12} {'Votes':>6}  {'Corr':>8}  {'MI':>8}  {'F':>10}  {'RF Imp':>10}  {'Lasso':>10}"
print(header)
print("    " + "-" * 68)
for feat in vote_series[vote_series >= 2].index:
    corr_v   = corr_series.get(feat, float("nan"))
    mi_v     = mi_series.get(feat, float("nan"))
    f_v      = f_series.get(feat, float("nan"))
    rf_v     = rf_series.get(feat, float("nan"))
    lasso_v  = lasso_coef.get(feat, float("nan"))
    print(f"    {feat:<12} {vote_counts[feat]:>6}  {corr_v:>8.4f}  {mi_v:>8.4f}  {f_v:>10.2f}  {rf_v:>10.4f}  {lasso_v:>10.6f}")

print("\n" + "=" * 70)
print("  Done. All plots saved to:", PLOTS_DIR)
print("=" * 70)
