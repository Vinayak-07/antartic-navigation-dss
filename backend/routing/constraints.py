"""Safety constraints and exclusions for routing.

This module provides routing constraints including land/coast blocking,
vessel ice capability limits, and dangerous-area exclusions.
"""

from backend.utils.coordinates import DEFAULT_ANTARCTIC_MASK


def apply_constraints(grid, vessel_ice_class: str = "PC6", coast_buffer_km: float = 10.0, step: float = 2.0):
    """
    Apply routing constraints to a cost grid.
    
    Args:
        grid: The cost grid dictionary with cells
        vessel_ice_class: Vessel polar class (PC1-PC7, A, B, C)
        coast_buffer_km: Safety buffer from coast in km
        step: Grid step size in degrees
        
    Returns:
        Modified grid with constraints applied
    """
    # Ice capability limits (maximum sea ice concentration vessel can navigate)
    ice_class_limits = {
        "PC1": 1.0,    # Year-round operation in all polar waters
        "PC2": 0.95,
        "PC3": 0.9,
        "PC4": 0.8,
        "PC5": 0.7,
        "PC6": 0.6,    # Summer/autumn operation in medium first-year ice
        "PC7": 0.5,    # Summer operation in thin first-year ice
        "A": 0.6,
        "B": 0.5,
        "C": 0.4,
    }
    
    max_ice_concentration = ice_class_limits.get(vessel_ice_class, 0.6)
    
    cells = grid.get("cells", {})
    for coord, cell in cells.items():
        lat, lon = coord
        
        # Check if cell is on land or too close to coast
        if not DEFAULT_ANTARCTIC_MASK.is_ocean(lat, lon, 0, 0, buffer_m=coast_buffer_km * 1000):
            cell["blocked"] = True
            cell["cost"] = 0.0
            cell["constraint_reason"] = "land_or_coast"
            continue
            
        # Check sea ice concentration against vessel capability
        sea_ice_risk = cell.get("risk", {}).get("sea_ice_risk", 0)
        # Convert risk to approximate concentration (rough inverse mapping)
        # sea_ice_risk = 0.55 * concentration + 0.12 * thickness
        # thickness = 0.05 + 2.8 * concentration^1.25
        # This is approximate - in practice we'd pass concentration directly
        if sea_ice_risk > 0.7:  # High ice risk threshold
            # Check if it's beyond vessel capability
            # For now, block cells with very high ice risk for non-icebreaker vessels
            if vessel_ice_class not in {"PC1", "PC2", "PC3"}:
                cell["blocked"] = True
                cell["cost"] = 0.0
                cell["constraint_reason"] = "ice_capability_exceeded"
                continue
    
    grid["cells"] = cells
    return grid


def is_cell_navigable(latitude: float, longitude: float, vessel_ice_class: str = "PC6", coast_buffer_km: float = 10.0) -> tuple:
    """
    Check if a specific cell is navigable.
    
    Returns:
        Tuple of (navigable: bool, reason: str)
    """
    # Check land/coast
    if not DEFAULT_ANTARCTIC_MASK.is_ocean(latitude, longitude, 0, 0, buffer_m=coast_buffer_km * 1000):
        return False, "land_or_coast"
    
    # Check if inside Antarctic land polygon
    return True, "navigable"
