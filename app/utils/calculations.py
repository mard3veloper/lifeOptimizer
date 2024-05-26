import math
from itertools import combinations

def calculate_number_of_possible_states(variables, num_vars, order_matters):
    total_states = 0
    for variable_combination in combinations(variables, num_vars):
        states_for_combination = 1
        for var in variable_combination:
            states_for_combination *= len(var['possible_values'])
        if order_matters:
            states_for_combination *= math.factorial(num_vars)
        total_states += states_for_combination
    return total_states
