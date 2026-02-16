from typing import Any

from src.utils.numbers import resolve_positive_int


def get_parameters(params_cfg: dict[str, Any]) -> dict[str, Any]:
    """Extract simulation parameters with safe optional keys."""
    return {
        "items": params_cfg["items"],
        "suppressed": params_cfg["suppressed"],
        "completion_requirement": params_cfg["completion_requirement"],
        "early_shift_factors": params_cfg["early_shift_factors"],
        "late_shift_factors": params_cfg["late_shift_factors"],
        "call_horizon_days": params_cfg["call_horizon_days"],
        "basic_start_date": params_cfg.get("basic_start_date"),
        "annual_estimate_recalculate_after_days": resolve_positive_int(
            params_cfg.get("annual_estimate_recalculate_after_days", 100),
            default=100,
        ),
    }
