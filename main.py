from simulation.config_loader import load_config, generate_parameter_combinations
from simulation.montecarlo import build_counter_data, run_simulation, build_work_order_schedule
from simulation.results import summarize_results
import matplotlib.pyplot as plt
        
plot = True
if __name__ == "__main__":
    config = load_config("config.json")
    df = build_counter_data(config)
    
    parameters = generate_parameter_combinations(config["parameters"])
    dfs = []
    for param_set in parameters[:1]:
        df = run_simulation(df, param_set)
        df = df[df['completion'] == True] 
        df['cumsum_package_cycle'] = df['package_cycle'].cumsum()
        
        if plot:
            # plot the df column next_planned_counter vs call_number
            plt.figure(figsize=(10, 6))
            plt.plot(df['call_number'], df['next_planned_counter'], marker='o')
            plt.plot(df['call_number'], df['cumsum_package_cycle'], marker='x')
            plt.xlabel('Call Number')
            plt.ylabel('Next Planned Counter')
            plt.title('Next Planned Counter vs Call Number')
            plt.grid()
            
            plt.show() 
        