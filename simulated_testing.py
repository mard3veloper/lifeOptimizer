import json
import random
import matplotlib.pyplot as plt
from reinforcement_learning import ReinforcementLearning
from hill_climbing import HillClimbing
from genetic_algo import GeneticAlgo
from random_comparison import RandomComparison
from test_generator import TestGenerator

def load_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def save_data(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def find_utility_value(variables, utility_data):
    query_state = {var['name']: var['value'] == 'True' for var in variables}
    for entry in utility_data:
        if entry['state'] == query_state:
            return entry['utility_value']
    return None
# just for json formatting
def format_state_utility(title, description, utility_value, algorithm, variables, iteration_count):
    return {
        "title": title,
        "description": description,
        "utility_measure": {
            "name": "Utility",
            "value": utility_value
        },
        "algorithm": convert_Algorithm_to_string(algorithm),
        "variables": variables,
        "iteration_count": iteration_count
    }

# automatically generate test data and simulate the set of algorithms
def simulate_algorithm_test(input_filename, paramaterMapSize, algorithms, num_iterations):
    
    utility_data = load_data(input_filename)
    initial_state = random.choice(utility_data)
    output_file_names = []

    for algo in algorithms:
        # this section mostly for saving initial state to have the algorithm start from a known state
        output_file = f"test_output_{paramaterMapSize}_{convert_Algorithm_to_string(algo)}_{num_iterations}.json"
        output_file_names.append(output_file)
        test_results = []
        formatted_test_utility_values = format_state_utility('', '', initial_state['utility_value'], algo, [{"name": key, "value": str(val), "type": "boolean"} for key, val in initial_state['state'].items()], 1)
        test_results.append(formatted_test_utility_values)
        save_data(test_results, output_file)
        algo_instance = algo()

        # Run the algorithm for the specified number of iterations
        for i in range(1, num_iterations):
            new_params = algo_instance.next_parameters(output_file)
            new_variables = [{"name": name, "value": value, "type": "boolean"} for name, value in new_params.items()]
            # if algo == ReinforcementLearning:
            #     print(new_params)
            utility_value = find_utility_value(new_variables, utility_data)

            formatted_test_result = format_state_utility(
                f"Test Iteration {i+1}",
                "",
                utility_value if utility_value is not None else 'Utility not found',
                algo,
                new_variables,
                i+1
            )
            test_results.append(formatted_test_result)

            save_data(test_results, output_file)  # This ensures data is saved at each step
    return output_file_names


def find_max_utility_value(data):
    valid_values = [float(item['utility_measure']['value']) for item in data if isinstance(item['utility_measure']['value'], (int, float))]
    return max(valid_values) if valid_values else None


def convert_Algorithm_to_string(algorithm):
    return str(algorithm).split('.')[1].split('\'')[0]

paramMapNumber = [6, 8, 10]
testedIterations = [10, 50, 100]
testedAlgorithms = [HillClimbing, RandomComparison, GeneticAlgo, ReinforcementLearning]
testGenerator = TestGenerator()
variation = 20
testFiles = []
all_output_files = []  # This will store all output file names across all simulations
for paramMap in paramMapNumber:
    testGenerator.generate_full_data(paramMap, variation, "mock_data_" + str(paramMap) + ".json")
    testFiles.append(["mock_data_" + str(paramMap) + ".json", str(paramMap)])
# Ensure all data generation and saving is completed before attempting to load and analyze
for testFile in testFiles:
    fileName = testFile[0]
    strparamMap = testFile[1]
    for iteration in testedIterations:
        outputFiles = simulate_algorithm_test(fileName, strparamMap, testedAlgorithms, iteration)
        all_output_files.extend(outputFiles)  # Extend the cumulative list with new file names

# # Now process and print the max utility value for each output file
for outputFile in all_output_files:
    try:
        data = load_data(outputFile)
        print(f"Max Utility Value in {outputFile}: {find_max_utility_value(data)}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
