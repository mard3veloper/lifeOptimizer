import numpy as np
import json

class TestGenerator:
    # this is the seed value
    def initialize_state(self, num_params):
        # Generate a random initial state with a random utility value
        initial_state = tuple(np.random.choice([True, False]) for _ in range(num_params))
        utility_values = {initial_state: np.random.uniform(1, 100)}
        return initial_state, utility_values
    # this function generates the neighbors of the current state essentualy using wave collapse algorithm
    def generate_neighbors(self, state):
        num_params = len(state)
        return [tuple(state[i] if i != idx else not state[i] for i in range(num_params)) for idx in range(num_params)]
    # this function generates the utility values for the states within the range
    def generate_utility_values(self, initial_state, num_params, variation_range, utility_values):
        states_to_process = [initial_state]
        processed_states = set()

        while states_to_process:
            current_state = states_to_process.pop(0)
            if current_state in processed_states:
                continue
            processed_states.add(current_state)

            neighbors = self.generate_neighbors(current_state)
            for neighbor in neighbors:
                if neighbor not in utility_values:
                    neighbor_neighbors = self.generate_neighbors(neighbor)
                    defined_neighbors = [n for n in neighbor_neighbors if n in utility_values]

                    if defined_neighbors:
                        average_utility = np.mean([utility_values[n] for n in defined_neighbors])
                        # Smoother transition: Gaussian variation with decreasing scale
                        scale = variation_range / (1 + len(defined_neighbors))  # Smaller scale as more neighbors are defined
                        random_variation = np.random.normal(0, scale)  # Gaussian variation
                        utility_values[neighbor] = np.clip(average_utility + random_variation, 1, 100)
                        states_to_process.append(neighbor)

    def save_utilities_to_json(self,utility_values, num_params, filename):
        variable_names = [f"Var_{i+1}" for i in range(num_params)]
        data = []
        for state, value in sorted(utility_values.items()):
            state_dict = {variable_names[i]: bool(state[i]) for i in range(num_params)}
            neighbors = self.generate_neighbors(state)
            neighbor_data = {
                str({variable_names[i]: bool(n[i]) for i in range(num_params)}): utility_values.get(n, 'Not yet calculated')
                for n in neighbors
            }
            entry = {
                "state": state_dict,
                "utility_value": value,
                "neighbors": neighbor_data
            }
            data.append(entry)

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=False)

    def generate_full_data(self, num_params, variation_range, filename):
        initial_state, utility_values = self.initialize_state(num_params)
        self.generate_utility_values(initial_state, num_params, variation_range, utility_values)
        self.save_utilities_to_json(utility_values, num_params, filename)