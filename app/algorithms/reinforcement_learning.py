import random
from algorithms.optimization_algorithm import OptimizationAlgorithm
import json
import numpy as np

class ReinforcementLearning(OptimizationAlgorithm):
    """
    Simulates the hill climbing algorithm.
    Currently, it returns a random state for testing purposes.

    :param variables: a list of variable names
    """
    #Defining the different parameters
    
    
    #Initializing the Q-matrix
    def next_parameters(self, filename):
        epsilon = 0.9
        alpha = 0.85
        gamma = 0.95
        with open(filename, 'r') as file:
            data = json.load(file)
        length = 2**len(data[-1]['variables'])
        variables = data[-1]['variables']
        if data[-1]['iteration_count'] == 1:
            Q = np.zeros((length, length-1))
            state = 0
            num = 0
             # Assuming data is sorted and last entry is latest
            for var in variables:
                if var['value'] == "True":
                    state += 2**num
                num += 1  
        else:
            with open('Reinforcement.json', 'r') as file:
                table = json.load(file)
            Q = np.array(table['Q'])
            num = 0
            state = 0
            pvariables = data[len(data)-1]['variables']
            for var in pvariables:
                if var['value'] == "True":
                    state += 2**num
                num += 1
            next_state = 0
            old_value = Q[state, table['action']]
            num = 0
            for var in variables:
                if var['value'] == "True":
                    next_state += 2**num
                num += 1
            
            next_max = np.max(Q[next_state])
            if isinstance(data[-1]['utility_measure']['value'], int):
                new_value = (1-alpha)*old_value + alpha*(int(data[-1]['utility_measure']['value']) + gamma*next_max)
                Q[state, table['action']] = new_value
            state = next_state
        
        # print(data)
        # print()

        # Assuming each variable block contains a 'name' and expecting it to be boolean
        new_params = {}
        try:
            
            action=0
            if np.random.uniform(0, 1) < epsilon:
                action = random.randint(0, length-2)
            else:
                action = np.argmax(Q[state, :])
            baction = bin(action+1)
            for var in variables:
                if(len(baction) > 1 and baction[len(baction)-1] == '1'):
                    new_params[var['name']] = "True" if var['value'] == "False" else "False"
                else:
                    new_params[var['name']] = "True" if var['value'] == "True" else "False"
                baction = baction[:-1]
            rldata = {"Q": Q.tolist(),
                      "action": int(action)}
            with open('Reinforcement.json', 'w') as f:
                json.dump(rldata, f)  
        except (IndexError, KeyError) as e:
            print(f"Error accessing variables from JSON data: {e}")
        
        return new_params