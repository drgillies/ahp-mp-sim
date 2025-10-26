def get_parameters(params_cfg: dict) -> dict:
    """Extract SAP maintenance parameters for simulation."""
    return {
        "items": params_cfg["items"],
        "suppressed": params_cfg["suppressed"],
        "completion_requirement": params_cfg["completion_requirement"],
        "early_shift_factors": params_cfg["early_shift_factors"],
        "late_shift_factors": params_cfg["late_shift_factors"],
        "call_horizon_days": params_cfg["call_horizon_days"],
        "basic_start_date": params_cfg["basic_start_date"],
    }
