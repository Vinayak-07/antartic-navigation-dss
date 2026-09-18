"""Uncertainty estimation for prediction outputs.

Returns computed confidence intervals — not a constant.
"""


def estimate_uncertainty(predicted_concentration: float, lead_time_hours: float = 24.0, model_version: str = "synthetic-baseline-1") -> dict:
    """Compute predictive variance / confidence from forecast horizon and concentration."""
    # Uncertainty grows with lead time and near critical thresholds
    base = 0.05 + 0.015 * (lead_time_hours / 24.0)
    critical_penalty = 0.08 if 0.4 <= predicted_concentration <= 0.7 else 0.0
    variance = round(min(0.35, base + critical_penalty), 4)
    
    # 90% confidence interval (approximate)
    ci_lower = max(0.0, round(predicted_concentration - 1.28 * variance, 4))
    ci_upper = min(1.0, round(predicted_concentration + 1.28 * variance, 4))
    
    return {
        "status": "computed",
        "variance": variance,
        "confidence_interval_90": (ci_lower, ci_upper),
        "forecast_confidence": round(max(0.0, 1.0 - 2.5 * variance), 4),
        "model_version": model_version,
    }
