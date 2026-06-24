# utils/data_loader.py

import pandas as pd
from ucimlrepo import fetch_ucirepo
from config.settings import TARGET_COLUMN


def load_dataset():
    print("[DataLoader] 📥 Fetching UCI dataset (id=697)...")
    dataset = fetch_ucirepo(id=697)

    X = dataset.data.features
    y = dataset.data.targets

    df = pd.concat([X, y], axis=1)

    # ── Target ────────────────────────────────
    target_col = [c for c in df.columns if c.lower() == "target"]
    if target_col:
        df[TARGET_COLUMN] = (df[target_col[0]] == "Dropout").astype(int)
        df.drop(columns=target_col, inplace=True)

    # ── Clean column names ────────────────────
    # Spaces→underscore, remove parens, slashes
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r"[/\\\(\)\-]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
    )

    print("[DataLoader] Cleaned columns sample:", list(df.columns[:5]))

    df = df.dropna()

    # ── Use all numeric features ──────────────
    feature_columns = [c for c in df.select_dtypes(include="number").columns
                       if c != TARGET_COLUMN]

    print(f"[DataLoader] ✅ Loaded {len(df)} students | "
          f"Features: {len(feature_columns)} | "
          f"Dropout rate: {df[TARGET_COLUMN].mean()*100:.1f}%")

    # ── Print key columns so Agent 2 can use exact names ──
    key_hint = [c for c in feature_columns if "sem" in c.lower() or "curricular" in c.lower()]
    if key_hint:
        print(f"[DataLoader] Key academic columns: {key_hint}")

    return df, feature_columns


def get_sample_student(df: pd.DataFrame, feature_columns: list, at_risk: bool = True) -> dict:
    subset = df[df[TARGET_COLUMN] == (1 if at_risk else 0)]
    row    = subset.sample(1, random_state=42).iloc[0].to_dict()
    row["student_id"] = "STU_REAL_001" if at_risk else "STU_REAL_002"
    return row