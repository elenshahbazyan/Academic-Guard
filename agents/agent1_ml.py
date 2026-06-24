# agents/agent1_ml.py
# ── Agent 1: Random Forest ────────────────────
# Single algorithm — clean, explainable, CPU-friendly
# Produces feature importances → used by Agent 2

import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

from config.settings import TARGET_COLUMN

MODEL_PATH = "outputs/model.joblib"


class MLAgent:

    def __init__(self):
        self.model               = None
        self.scaler              = StandardScaler()
        self.trained             = False
        self.feature_columns     = []
        self.feature_importances = {}

    # ── Train ─────────────────────────────────

    def train(self, df: pd.DataFrame, feature_columns: list) -> dict:
        print("[Agent 1] Training Random Forest...")

        self.feature_columns = feature_columns

        X = df[feature_columns]
        y = df[TARGET_COLUMN]

        # 80% train, 20% test — stratified to keep same dropout rate in both
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size    = 0.2,
            random_state = 42,
            stratify     = y
        )

        # Scale features so all are on same range (mean=0, std=1)
        X_train = self.scaler.fit_transform(X_train)
        X_test  = self.scaler.transform(X_test)

        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators = 200,      # 200 trees
            max_depth    = None,     # trees grow until pure leaves
            random_state = 42,
            n_jobs       = -1        # use all CPU cores
        )
        self.model.fit(X_train, y_train)

        # ── Evaluate ──────────────────────────
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        auc    = roc_auc_score(y_test, y_prob)
        report = classification_report(y_test, y_pred, output_dict=True)

        # ── Feature importances ───────────────
        # How much each feature reduced prediction error across all 200 trees
        importances = self.model.feature_importances_
        self.feature_importances = dict(
            sorted(
                zip(feature_columns, importances),
                key=lambda x: x[1],
                reverse=True
            )
        )

        self.trained = True
        self._save()

        metrics = {
            "auc":      round(auc, 4),
            "accuracy": round(report["accuracy"], 4),
            "f1":       round(report["1"]["f1-score"], 4),
        }

        print(f"[Agent 1] ✅ Done — AUC: {metrics['auc']} | "
              f"Accuracy: {metrics['accuracy']} | F1: {metrics['f1']}")
        print(f"[Agent 1] Top 5 features: "
              f"{list(self.feature_importances.keys())[:5]}")
        return metrics

    # ── Predict ───────────────────────────────

    def predict(self, student: dict) -> dict:
        """Score a single student. Returns risk score 0-100 + top features."""

        # Build feature row in correct order
        features = pd.DataFrame(
            [[student.get(f, 0) for f in self.feature_columns]],
            columns=self.feature_columns
        )

        # Scale using the same scaler from training
        scaled = self.scaler.transform(features)

        # Get dropout probability from Random Forest
        prob       = self.model.predict_proba(scaled)[0][1]
        risk_score = round(prob * 100, 1)

        # Top 5 most important features for this prediction
        top_factors = [
            {
                "feature":    f,
                "value":      student.get(f, "N/A"),
                "importance": round(imp, 4)
            }
            for f, imp in list(self.feature_importances.items())[:5]
        ]

        result = {
            "agent":       "Agent 1 — Random Forest",
            "risk_score":  risk_score,
            "verdict":     self._label(risk_score),
            "top_factors": top_factors,
        }

        print(f"[Agent 1] Risk Score: {risk_score}/100 → {result['verdict']}")
        print(f"[Agent 1] Top risk factor: "
              f"{top_factors[0]['feature']} = {top_factors[0]['value']}")
        return result

    # ── Helpers ───────────────────────────────

    def _label(self, score: float) -> str:
        if score < 40: return "LOW"
        if score < 60: return "MEDIUM"
        if score < 80: return "HIGH"
        return "CRITICAL"

    def _save(self):
        os.makedirs("outputs", exist_ok=True)
        joblib.dump({
            "model":           self.model,
            "scaler":          self.scaler,
            "importances":     self.feature_importances,
            "feature_columns": self.feature_columns,
        }, MODEL_PATH)
        print(f"[Agent 1] Model saved → {MODEL_PATH}")

    def load(self):
        if os.path.exists(MODEL_PATH):
            data = joblib.load(MODEL_PATH)
            self.model               = data["model"]
            self.scaler              = data["scaler"]
            self.feature_importances = data["importances"]
            self.feature_columns     = data["feature_columns"]
            self.trained             = True
            print("[Agent 1] Model loaded from disk.")