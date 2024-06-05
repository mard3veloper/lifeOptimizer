import random
import json
import os
from app.algorithms.optimization_algorithm import OptimizationAlgorithm

class HillClimbingOptimization(OptimizationAlgorithm):

    def initialize_impacts(self, impacts_filepath, variables):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(impacts_filepath), exist_ok=True)
        
        impacts = {
            "impact_scores": {var['name']: {"score": "NA", "iteration_count": 1} for var in variables},
            "impact_testing_state": True
        }
        with open(impacts_filepath, 'w') as f:
            json.dump(impacts, f)

    def load_impacts(self, impacts_filepath):
        if os.path.exists(impacts_filepath):
            with open(impacts_filepath, 'r') as f:
                return json.load(f)
        return None

    def save_impacts(self, impacts_filepath, impacts):
        with open(impacts_filepath, 'w') as f:
            json.dump(impacts, f)

    def variable_impact_testing_state(self, initial_state, impacts, data, impacts_filepath):
        for var in initial_state['variables']:
            if impacts["impact_scores"][var['name']]["score"] == "NA":
                new_params = {v['name']: v['current_value'] for v in initial_state['variables']}
                if var['type'] == 'Boolean':
                    new_params[var['name']] = not var['current_value']
                elif var['type'] == 'Categorical':
                    new_params[var['name']] = random.choice([val for val in var['possible_values'] if val != var['current_value']])
                elif var['type'] == 'Numerical':
                    current_value = int(var['current_value'])
                    possible_values = var['possible_values']
                    if current_value == possible_values[0]:
                        new_params[var['name']] = current_value + 1
                    elif current_value == possible_values[-1]:
                        new_params[var['name']] = current_value - 1
                    else:
                        new_params[var['name']] = random.choice([current_value - 1, current_value + 1])
                # Ensure the new_params state has not been tested
                if not self.state_already_tested(new_params, data):
                    return new_params
        impacts['impact_testing_state'] = False
        self.save_impacts(impacts_filepath, impacts)
        return None

    def next_parameters(self, filename, problem_title):
        with open(filename, 'r') as file:
            data = json.load(file)
        
        variables = data[-1]['variables']

        impacts_filename = f"problems/impacts/{problem_title}_impacts.json"
        current_path = os.getcwd()
        impacts_filepath = os.path.join(current_path, impacts_filename)

        if len(data) == 1:
            self.initialize_impacts(impacts_filepath, variables)
        
        impacts = self.load_impacts(impacts_filepath)

        if len(data) > 1:
            self.update_impacts(data, impacts, impacts_filepath)
            impacts = self.load_impacts(impacts_filepath)

        if impacts['impact_testing_state']:
            print("IMPACT TESTING STATE")
            potential_next_params = self.variable_impact_testing_state(data[0], impacts, data, impacts_filepath)
            if potential_next_params is not None:
                return potential_next_params
        
        print("OUT OF IMPACT TESTING STATE")
        
        potential_next_params = self.hill_climbing_step(data, variables, impacts)

        if potential_next_params is not None:
            return potential_next_params
        
        for state in data:
            state['fully_explored'] = True
        self.update_json(filename, data)

        # If all states are explored, return a message indicating this
        if all(state['fully_explored'] for state in data):
            print("All possible states explored.")
            return "All possible states explored."

        new_params = self.generate_random_state(variables)

        attempts = 0
        max_attempts = 100  # To prevent infinite loop
        while self.state_already_tested(new_params, data):
            new_params = self.generate_random_state(variables)
            attempts += 1
            if attempts >= max_attempts:
                print("All possible states explored.")
                return "All possible states explored."
        return new_params

    def update_impacts(self, data, impacts, impacts_filepath):
        last_state = data[-1]
        previous_state = data[-2]
        change_in_utility = abs(last_state['optimized_variable']['value'] - previous_state['optimized_variable']['value'])

        for var in last_state['variables']:
            if var['current_value'] != [v for v in previous_state['variables'] if v['name'] == var['name']][0]['current_value']:
                var_name = var['name']
                iteration_count = impacts["impact_scores"][var_name]["iteration_count"]
                current_score = impacts["impact_scores"][var_name]["score"]
                if current_score == "NA":
                    new_score = change_in_utility
                else:
                    new_score = ((current_score * (iteration_count - 1)) + change_in_utility) / iteration_count
                impacts["impact_scores"][var_name]["score"] = new_score
                impacts["impact_scores"][var_name]["iteration_count"] += 1
                self.save_impacts(impacts_filepath, impacts)
                break

    def hill_climbing_step(self, data, variables, impacts):
        best_state = max([state for state in data if not state['fully_explored']], key=lambda x: x['optimized_variable']['value'], default=None)
        
        if best_state is None:
            new_params = self.generate_random_state(variables)
            while self.state_already_tested(new_params, data):
                new_params = self.generate_random_state(variables)
            return new_params

        for var in sorted(impacts["impact_scores"], key=lambda x: impacts["impact_scores"][x]["score"], reverse=True):
            potential_values = []
            for value in [v for v in variables if v['name'] == var][0]['possible_values']:
                if value != [v for v in variables if v['name'] == var][0]['current_value']:
                    new_params = self.generate_new_state(best_state['variables'], var, value)
                    if not self.state_already_tested(new_params, data):
                        potential_values.append(value)

            if len(potential_values) == 1:
                return self.generate_new_state(best_state['variables'], var, potential_values[0])
            elif len(potential_values) > 1:
                last_utility_change = data[-1]['optimized_variable']['value'] - data[-2]['optimized_variable']['value']
                if [v for v in variables if v['name'] == var][0]['type'] == 'Categorical':
                    return self.generate_new_state(best_state['variables'], var, random.choice(potential_values))
                elif [v for v in variables if v['name'] == var][0]['type'] == 'Numerical':
                    current_value = int([v for v in best_state['variables'] if v['name'] == var][0]['current_value'])
                    possible_values = [int(v) for v in [v for v in variables if v['name'] == var][0]['possible_values']]
                    previous_value = int([v for v in data[-2]['variables'] if v['name'] == var][0]['current_value'])
                    direction = 1 if last_utility_change > 0 else -1
                    current_index = possible_values.index(current_value)
                    new_index = current_index + direction
                    if new_index < 0:
                        new_index = 0
                    elif new_index >= len(possible_values):
                        new_index = len(possible_values) - 1
                    return self.generate_new_state(best_state['variables'], var, possible_values[new_index])

    def generate_new_state(self, variables, var_name, new_value):
        new_state = {var['name']: self.convert_to_correct_type(var['current_value'], var['type']) for var in variables}
        new_state[var_name] = self.convert_to_correct_type(new_value, [v for v in variables if v['name'] == var_name][0]['type'])
        return new_state

    def convert_to_correct_type(self, value, var_type):
        if var_type == 'Boolean':
            return value == 'True' if isinstance(value, str) else bool(value)
        elif var_type == 'Numerical':
            return int(value)
        elif var_type == 'Categorical':
            return str(value)
        return value

    def generate_random_state(self, variables):
        return {var['name']: self.convert_to_correct_type(random.choice(var['possible_values']), var['type']) for var in variables}

    def state_already_tested(self, new_state, data):
        for state in data:
            if all(self.convert_to_correct_type(state['variables'][i]['current_value'], state['variables'][i]['type']) == self.convert_to_correct_type(new_state[state['variables'][i]['name']], state['variables'][i]['type']) for i in range(len(state['variables']))):
                return True
        return False

    def update_json(self, filename, data):
        with open(filename, 'w') as file:
            json.dump(data, file)
