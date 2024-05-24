import random
import json
from optimization_algorithm import OptimizationAlgorithm

class HillClimbing(OptimizationAlgorithm):
    """
    Implements the hill climbing algorithm with systematic single-variable modifications.
    Commits to exploring a random state until a local max is reached.
    """

    def __init__(self):
        self.current_best = None  # Tracks the current best state during exploration
        self.exploring_random = False  # Indicates if we are exploring from a random state

    def next_parameters(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)

        if not data:
            return {'variable1': 'True'}  # Return a default if no data

        # check if we are in the first iteration
        if self.current_best is None:
            # Find the state with the highest utility so far
            best_state = max(data, key=lambda x: x['utility_measure']['value'])

        # if we have reached local max, continue exploring from this state, else continue from the current best state
        else:
            if self.exploring_random:
                best_state = data[-1]  # Continue with the current best state if exploring a random path
            else:
                if data[-1]['utility_measure']['value'] > self.current_best['utility_measure']['value']:
                    # Continue with the current best state if exploring a random path
                    best_state = data[-1]

                else:
                    # Continue with the current best state if exploring a random path
                    best_state = self.current_best

        new_params = self.generate_next_unique_state(best_state, data)

        return new_params

    def generate_next_unique_state(self, best_state, data):
        variables = best_state['variables']
        original_values = {var['name']: var['value'] for var in variables}  # Save original values

        # systematic single-variable modifications
        for i, var in enumerate(variables):
            # Try flipping the current variable
            new_params = original_values.copy()
            new_params[var['name']] = "False" if var['value'] == "True" else "True"

            # Check if the new state is unique
            if not any(self.is_same_state(new_params, entry['variables']) for entry in data):
                # self.current_best = {'variables': [dict(name=k, value=v) for k, v in new_params.items()],
                #                      'utility_measure': best_state['utility_measure']}  # Update current best
                return new_params  # Return new state if it's unique

        # If no unique state was found, start exploring a random state (local max reached)
        random_state = self.generate_random_state(variables)
        return random_state

    def generate_random_state(self, variables):
        random_state = {var['name']: random.choice(["True", "False"]) for var in variables}
        self.exploring_random = True
        return random_state

    def is_same_state(self, new_params, old_params):
        return all(new_params.get(var['name']) == var['value'] for var in old_params)

