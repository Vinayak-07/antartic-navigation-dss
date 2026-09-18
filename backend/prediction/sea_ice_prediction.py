"""Sea-ice prediction baseline module.

Baseline: persistence + physics-informed temporal advection.
Not a real satellite-fed model — clearly labelled synthetic.
"""

from backend.scientific import SeaIceModel, SyntheticEnvironmentProvider


def predict_sea_ice(latitude: float, longitude: float, lead_time_hours: float = 24.0, environment_provider: SyntheticEnvironmentProvider = None, seed: int = 101) -> dict:
    """
    Baseline prediction interface for sea-ice concentration.
    
    Returns:
        lead_time_hours
        predicted_concentration (0-1)
        predicted_category (machine-readable)
        predicted_thickness_m
        navigability
        risk_score
        uncertainty (computed MAE proxy against persistence baseline)
    """
    # Use persistence baseline: current concentration + temporal drift
    if environment_provider is None:
        environment_provider = SyntheticEnvironmentProvider(seed, "NORMAL")
    
    sea_ice = SeaIceModel(environment_provider)
    current = sea_ice.concentration(latitude, longitude, 0.0)
    
    # Simple temporal advection baseline: drift with seasonal/inter-annual signal
    temporal_shift = 0.02 * (lead_time_hours / 24.0) * (1.0 if latitude > -65 else -0.5)
    predicted = max(0.0, min(1.0, current + temporal_shift))
    
    # Canonical categories
    def category(conc):
        if conc < 0.1: return "OPEN_WATER"
        if conc < 0.3: return "VERY_OPEN_ICE"
        if conc < 0.5: return "OPEN_ICE"
        if conc < 0.7: return "CLOSE_ICE"
        if conc < 0.9: return "VERY_CLOSE_ICE"
        return "FAST_ICE"
    
    category_label = category(predicted)
    thickness = 0.05 + 2.8 * (predicted ** 1.25)
    navigability = "BLOCKED" if predicted > 0.8 else "RESTRICTED" if predicted > 0.6 else "OPEN"
    risk_score = round(min(1.0, 0.55 * predicted + 0.12 * thickness), 4)
    
    # Uncertainty proxy: difference from persistence
    uncertainty = round(min(0.4, abs(predicted - current) + 0.05), 4)
    
    return {
        "status": "baseline",
        "lead_time_hours": float(lead_time_hours),
        "predicted_concentration": round(predicted, 4),
        "predicted_category": category_label,
        "predicted_thickness_m": round(thickness, 4),
        "navigability": navigability,
        "risk_score": risk_score,
        "uncertainty": uncertainty,
        "model_version": "synthetic-baseline-1",
        "data_source": "synthetic-demonstration",
    }
