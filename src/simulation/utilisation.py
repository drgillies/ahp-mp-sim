import numpy as np

def generate_utilisation(
    dist_cfg: dict,
    num_simulations: int,
    num_days: int
):
    """
    Generate DAILY utilisation samples for all simulations, assets, and days.
    Supports multiple distributions starting at different days.
    Values are clipped to min and max if provided and rounded to 2 decimals.
    Shape: (num_simulations, num_assets, num_days)
    """
    # Initialise the array
    utilisation = np.zeros((num_simulations, num_days))
    
    # Sort phases by starting day
    phases = sorted(dist_cfg.values(), key=lambda x: x["after_day"])
    
    for i, phase in enumerate(phases):
        start_day = phase["after_day"]
        end_day = phases[i + 1]["after_day"] if i + 1 < len(phases) else num_days
        
        dist = phase["distribution"]
        
        if dist == "normal":
            vals = np.random.normal(
                loc=phase["mean"],
                scale=phase["std"],
                size=(num_simulations, end_day - start_day)
            )
        elif dist == "uniform":
            vals = np.random.uniform(
                low=phase["min"],
                high=phase["max"],
                size=(num_simulations, end_day - start_day)
            )
        elif dist == "poisson":
            vals = np.random.poisson(
                lam=phase["lambda"],
                size=(num_simulations, end_day - start_day)
            )
        else:
            raise ValueError(f"Unsupported distribution: {dist}")
        
        # Clip values if min/max are defined
        min_val = phase.get("min", None)
        max_val = phase.get("max", None)
        if min_val is not None or max_val is not None:
            vals = np.clip(vals, a_min=min_val, a_max=max_val)
        
        # Round to 2 decimal places
        vals = np.round(vals, 2)
        
        utilisation[:, start_day:end_day] = vals
    
    return utilisation
