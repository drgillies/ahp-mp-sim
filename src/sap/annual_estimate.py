def recalculate_annual_estimate(cumulative_list):
    """Recalculate the annual estimate based on simulation results."""
    if cumulative_list:
        return sum(cumulative_list) / len(cumulative_list) * 365
    return 0
