import json
import random

def load_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

class GeneticAlgo:
    def __init__(self):
        self.population = []
        self.parents = []
        # self.iteration_count = 0
        self.initialized = False

    # we need to start out with a population greater than 1, here we chose 4
    def initialize_population(self, filename):
        data = load_data(filename)
        initial_entry = data[0]
        self.population.append(initial_entry)
        # Generate three more entries randomly as the initla population
        for _ in range(3):
            random_entry = self.generate_random_state(initial_entry['variables'])
            self.population.append({
                'variables': random_entry,
                'utility_measure': {'value': None}
            })
        self.initialized = True

    def generate_random_state(self, variables_template):
        return [{'name': var['name'], 'value': random.choice(["True", "False"])} for var in variables_template]

    #as the json file is updated with the utility values, we need to update the population with the new utility values
    def update_population_with_new_utilities(self, filename):
        data = load_data(filename)
        for entry in self.population:
            if entry['utility_measure']['value'] is None:
                for data_entry in data:
                    if data_entry['variables'] == entry['variables']:
                        entry['utility_measure']['value'] = data_entry['utility_measure']['value']
                        break
    # swap the top and bottom values of the parents to create children
    def breed(self):
        # Assuming the population is sorted before this function is called
        parent1 = self.parents[0]['variables']
        parent2 = self.parents[1]['variables']
        child1, child2 = self.crossover(parent1, parent2)
        self.mutate(child1)
        self.mutate(child2)
        self.population.extend([
            {'variables': child1, 'utility_measure': {'value': None}},
            {'variables': child2, 'utility_measure': {'value': None}}
        ])

    def crossover(self, parent1, parent2):
        split_index = len(parent1) // 2
        # Ensure parents are dictionaries for easier manipulation
        child1 = {**{var['name']: var['value'] for var in parent1[:split_index]},
                **{var['name']: var['value'] for var in parent2[split_index:]}}
        child2 = {**{var['name']: var['value'] for var in parent2[:split_index]},
                **{var['name']: var['value'] for var in parent1[split_index:]}}
        return child1, child2

    # intruduce a mutation in the child
    def mutate(self, child):
        # Child is a dictionary
        mutation_variable = random.choice(list(child.keys()))
        child[mutation_variable] = not child[mutation_variable]  # Assuming boolean flip

    def next_parameters(self, filename):
        if not self.initialized:
            self.initialize_population(filename)
        else:
            self.update_population_with_new_utilities(filename)

        # Find the first entry without a set utility value
        for entry in self.population:
            if entry['utility_measure']['value'] is None:
                # Ensure that entry['variables'] is a dictionary
                return {var['name']: var['value'] for var in entry['variables']}

        # If all have utility values, breed the top two and continue
        self.population.sort(key=lambda x: x['utility_measure']['value'], reverse=True)
        self.parents = self.population[:2]
        self.breed()
        return self.next_parameters(filename)  # Recursively get the next parameters with new generation

