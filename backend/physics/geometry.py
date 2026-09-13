"""Iceberg geometry and mass calculations."""

ICE_DENSITY_KG_M3 = 917.0
ADDED_MASS_FACTOR = 1.15


def compute_geometry(length_m: float, width_m: float, height_m: float, density: float = ICE_DENSITY_KG_M3) -> dict:
    length = max(0.0, float(length_m))
    width = max(0.0, float(width_m))
    height = max(0.0, float(height_m))
    volume = length * width * height
    air_projected_area = length * height
    underwater_projected_area = length * max(width, height * 0.88)
    return {
        "volume_m3": volume,
        "mass_kg": volume * density,
        "projected_area_m2": air_projected_area,
        "air_projected_area_m2": air_projected_area,
        "underwater_projected_area_m2": underwater_projected_area,
        "waterline_area_m2": length * width,
        "draft_m": height * 0.88,
        "added_mass_factor": ADDED_MASS_FACTOR,
        "effective_mass_kg": volume * density * ADDED_MASS_FACTOR,
    }
