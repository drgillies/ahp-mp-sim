import matplotlib.pyplot as plt

from src.simulation.config_loader import generate_parameter_combinations, load_config
from src.simulation.montecarlo import build_counter_data, run_simulation


def main(plot: bool = True) -> None:
    config = load_config("config.json")
    counter_df = build_counter_data(config)
    parameter_sets = generate_parameter_combinations(config["parameters"])

    if not parameter_sets:
        print("No parameter combinations were generated.")
        return

    simulation_df = run_simulation(counter_df, parameter_sets[0], export_csv=True)
    completed_df = simulation_df[simulation_df["completion"] == True].copy()

    if completed_df.empty:
        print("No completed work orders found for the selected parameter set.")
        return

    completed_df["cumsum_package_cycle"] = completed_df["package_cycle"].cumsum()

    if plot:
        plt.figure(figsize=(10, 6))
        plt.plot(
            completed_df["call_number"],
            completed_df["next_planned_counter"],
            marker="o",
        )
        plt.plot(
            completed_df["call_number"],
            completed_df["cumsum_package_cycle"],
            marker="x",
        )
        plt.xlabel("Call Number")
        plt.ylabel("Next Planned Counter")
        plt.title("Next Planned Counter vs Call Number")
        plt.grid()
        plt.show()


if __name__ == "__main__":
    main()
