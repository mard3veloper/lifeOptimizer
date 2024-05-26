import random
import os
import json
print(os.getcwd())
from app.algorithms.optimization_algorithm import OptimizationAlgorithm
class RandomComparison(OptimizationAlgorithm):
    """
    Simulates a random choice of parameters for testing purposes.
    """

    def next_parameters(self, filename):
        
        with open(filename, 'r') as file:
            data = json.load(file)

        # Here is where we would implement an algorithm to determine the next set of parameters
        
        # for now, we will just return a random set of parameters
        new_params = {}
        try:
            variables = data[-1]['variables']  # Assuming data is sorted and last entry is latest
            for var in variables:
                if var["lock_value"]:
                    # If lock_value is True, keep the current value
                    new_params[var['name']] = var['current_value']
                else:
                    new_params[var['name']] = random.choice(var['possible_values'])
        except (IndexError, KeyError) as e:
            print(f"Error accessing variables from JSON data: {e}")
        
        return new_params