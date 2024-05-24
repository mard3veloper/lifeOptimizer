import random
from optimization_algorithm import OptimizationAlgorithm
import json

class RandomComparison(OptimizationAlgorithm):
    """
    Simulates the hill climbing algorithm.
    Currently, it returns a random state for testing purposes.

    :param variables: a list of variable names
    """

    def next_parameters(self, filename):
        
        with open(filename, 'r') as file:
            data = json.load(file)

        # print(data)
        # print()
        
        # Assuming each variable block contains a 'name' and expecting it to be boolean
        new_params = {}
        try:
            variables = data[-1]['variables']  # Assuming data is sorted and last entry is latest
            for var in variables:
                # Randomly assign True or False as strings, matching your JSON structure
                new_params[var['name']] = "True" if random.choice([True, False]) else "False"
        except (IndexError, KeyError) as e:
            print(f"Error accessing variables from JSON data: {e}")
        
        return new_params