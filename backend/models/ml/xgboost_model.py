from __future__ import annotations

from dataclasses import dataclass

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None

try:
    import shap
except Exception:  # pragma: no cover
    shap = None

try:
    import xgboost as xgb
except Exception:  # pragma: no cover
    xgb = None

from backend.utils.url_features import FEATURE_ORDER


@dataclass
class PredictionResult:
    probability: float
    shap_entries: list[dict[str, float | str]]


class XGBoostURLClassifier:
    def __init__(self) -> None:
        self.model = None
        self.explainer = None
        if xgb is not None and np is not None:
            self.model = xgb.XGBClassifier(
                n_estimators=32,
                max_depth=3,
                learning_rate=0.2,
                eval_metric="logloss",
            )
            sample_x = np.array(
                [
                    [15, 0, 0, 1, 2.0, 0, 0, 1, 0, -1],
                    [80, 3, 1, 7, 4.8, 1, 1, 0, 2, -1],
                    [54, 1, 0, 4, 4.0, 0, 1, 1, 0, -1],
                    [23, 0, 0, 0, 2.8, 0, 0, 1, 0, -1],
                ]
            )
            sample_y = np.array([0, 1, 1, 0])
            self.model.fit(sample_x, sample_y)
            if shap is not None:
                try:
                    self.explainer = shap.TreeExplainer(self.model)
                except Exception:
                    self.explainer = None

    def predict(self, features: dict[str, float]) -> PredictionResult:
        if self.model is None or np is None:
            probability = self._heuristic_probability(features)
            return PredictionResult(probability=probability, shap_entries=self._fallback_shap(features, probability))

        vector = np.array([[features[name] for name in FEATURE_ORDER]])
        probability = float(self.model.predict_proba(vector)[0][1])
        if self.explainer is None:
            return PredictionResult(probability=probability, shap_entries=self._fallback_shap(features, probability))

        try:
            shap_values = self.explainer.shap_values(vector)
            values = shap_values[0] if isinstance(shap_values, list) else shap_values[0]
            entries = [
                {
                    "feature": FEATURE_ORDER[index],
                    "value": float(vector[0][index]),
                    "contribution": float(values[index]),
                }
                for index in range(len(FEATURE_ORDER))
            ]
            entries.sort(key=lambda item: abs(float(item["contribution"])), reverse=True)
            return PredictionResult(probability=probability, shap_entries=entries[:5])
        except Exception:
            return PredictionResult(probability=probability, shap_entries=self._fallback_shap(features, probability))

    def _heuristic_probability(self, features: dict[str, float]) -> float:
        score = 0.0
        score += min(features["url_length"] / 120.0, 0.2)
        score += min(features["n_subdomains"] * 0.08, 0.2)
        score += features["has_ip_address"] * 0.2
        score += min(features["special_char_count"] * 0.03, 0.12)
        score += 0.12 if features["suspicious_tld"] else 0.0
        score += features["brand_mimic_score"] * 0.18
        score += min(max(features["entropy"] - 3.5, 0.0) * 0.08, 0.18)
        score += 0.06 if features["is_https"] == 0 else 0.0
        score += min(features["redirect_count"] * 0.08, 0.12)
        return max(0.01, min(score, 0.99))

    def _fallback_shap(self, features: dict[str, float], probability: float) -> list[dict[str, float | str]]:
        contributions = []
        for feature in FEATURE_ORDER:
            value = float(features[feature])
            weight = probability / max(len(FEATURE_ORDER), 1)
            if feature in {"brand_mimic_score", "has_ip_address", "suspicious_tld"}:
                weight *= 2
            contributions.append(
                {
                    "feature": feature,
                    "value": value,
                    "contribution": round(weight if value else -weight / 3, 4),
                }
            )
        contributions.sort(key=lambda item: abs(float(item["contribution"])), reverse=True)
        return contributions[:5]


def load_xgboost() -> XGBoostURLClassifier:
    return XGBoostURLClassifier()

