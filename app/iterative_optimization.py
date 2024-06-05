import json
import math
import sys
import os
from itertools import permutations
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QHBoxLayout
from PyQt5.QtGui import QDoubleValidator
from app.algorithms.random_comparison import RandomComparison
from app.algorithms.hill_climbing import HillClimbingOptimization

class IterativeOptimizationPage(QMainWindow):
    def __init__(self, app, problem_title, filename):
        super().__init__()
        self.app = app
        self.problem_title = problem_title
        self.filename = filename
        self.data = self.read_json(filename)
        # Default to the last iteration for manipulation
        if self.data:
            self.current_iteration = self.data[-1]  # Assuming there's at least one iteration
        else:
            self.current_iteration = None
        self.setWindowTitle("Iterative Optimization")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def read_json(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Check if there's a current iteration to display
        if self.current_iteration:
            # Display the title, description, and other details from the current iteration
            layout.addWidget(QLabel(f"Optimization for: {self.current_iteration['title']}"))
            layout.addWidget(QLabel(f"Description: {self.current_iteration['description']}"))
            self.iteration_count_label = QLabel(f"Number of Tested States: {self.current_iteration['iteration_count']}")
            layout.addWidget(self.iteration_count_label)
            self.num_states_label = QLabel(f"Number of Possible States: {self.current_iteration['calculated_states']}")
            layout.addWidget(self.num_states_label)
            layout.addWidget(QLabel(f"Optimization Option: {self.current_iteration['optimization_option']}"))

            # Display variables section
            layout.addWidget(QLabel("Variables:"))

            # Dynamically add labels and inputs for each variable
            self.variable_inputs = {}
            for var in self.current_iteration['variables']:
                var_layout = QHBoxLayout()
                var_label = QLabel(f"{var['name']}:")
                var_layout.addWidget(var_label)

                if var['type'] == 'Boolean':
                    var_combo = QComboBox(self)
                    var_combo.addItems(["True", "False"])
                    var_combo.setCurrentText("True" if var['current_value'] else "False")
                    var_layout.addWidget(var_combo)
                    self.variable_inputs[var['name']] = var_combo
                elif var['type'] == 'Numerical' or var['type'] == 'Categorical':
                    var_combo = QComboBox(self)
                    var_combo.addItems([str(value) for value in var['possible_values']])
                    var_combo.setCurrentText(str(var['current_value']))
                    var_layout.addWidget(var_combo)
                    self.variable_inputs[var['name']] = var_combo

                # Display the lock_value parameter as a dropdown
                lock_value_label = QLabel("Lock Value:")
                lock_value_combo = QComboBox(self)
                lock_value_combo.addItems(["True", "False"])
                lock_value_combo.setCurrentText("True" if var['lock_value'] else "False")
                lock_value_combo.currentIndexChanged.connect(self.recalculate_states)
                var_layout.addWidget(lock_value_label)
                var_layout.addWidget(lock_value_combo)
                self.variable_inputs[f"{var['name']}_lock_value"] = lock_value_combo

                # If order matters, display order and lock_order parameters as dropdowns
                if self.current_iteration['order_matters'] == "Yes":
                    order_label = QLabel(f"Order: {var['order']}")
                    var_layout.addWidget(order_label)

                    lock_order_label = QLabel("Lock Order:")
                    lock_order_combo = QComboBox(self)
                    lock_order_combo.addItems(["True", "False"])
                    lock_order_combo.setCurrentText("True" if var['lock_order'] else "False")
                    lock_order_combo.currentIndexChanged.connect(self.recalculate_states)
                    var_layout.addWidget(lock_order_label)
                    var_layout.addWidget(lock_order_combo)
                    self.variable_inputs[f"{var['name']}_lock_order"] = lock_order_combo

                layout.addLayout(var_layout)

            # Optimized variable input
            optimized_var_label = QLabel(f"Optimized Variable: {self.current_iteration['optimized_variable']['name']}")
            self.optimized_var_input = QLineEdit(self)
            self.optimized_var_input.setText(str(self.current_iteration['optimized_variable']['value']))
            self.optimized_var_input.setValidator(QDoubleValidator())  # Only allow numbers
            layout.addWidget(optimized_var_label)
            layout.addWidget(self.optimized_var_input)

            # Submit button
            submit_button = QPushButton("Submit")
            submit_button.clicked.connect(self.submit_data)
            layout.addWidget(submit_button)
        else:
            # If there are no iterations, display a message
            layout.addWidget(QLabel("No data available"))

    def toggle_boolean(self, variable_name, button):
        new_value = not button.isChecked()
        button.setText("True" if new_value else "False")
        self.variable_inputs[variable_name].setChecked(new_value)

    def recalculate_states(self):
        # Update current_iteration with the values from the UI
        for var in self.current_iteration['variables']:
            var['lock_value'] = self.variable_inputs[f"{var['name']}_lock_value"].currentText() == "True"
            if self.current_iteration['order_matters'] == "Yes":
                var['lock_order'] = self.variable_inputs[f"{var['name']}_lock_order"].currentText() == "True"
        new_num_states = self.calculate_possible_states()
        self.num_states_label.setText(f"Number of Possible States: {new_num_states}")

    def calculate_possible_states(self):
        num_vars_per_state = self.current_iteration['num_vars_per_state']
        locked_vars = [var for var in self.current_iteration['variables'] if var['lock_value']]
        unlocked_vars = [var for var in self.current_iteration['variables'] if not var['lock_value']]

        # Calculate initial possible states considering locked values
        initial_states = 1
        for var in unlocked_vars:
            initial_states *= len(var['possible_values'])

        # Calculate permutations if order matters and not locked
        if self.current_iteration['order_matters'] == "Yes":
            unlocked_order_vars = [var for var in unlocked_vars if not var['lock_order']]
            num_order_vars = len(unlocked_order_vars)
            order_states = math.factorial(num_order_vars)
        else:
            order_states = 1

        return initial_states * order_states

    def calculate_tested_states(self):
        count = 0
        for state in self.data:
            match = True
            for var in state['variables']:
                current_var = next(v for v in self.current_iteration['variables'] if v['name'] == var['name'])
                if current_var['lock_value'] and current_var['current_value'] != var['current_value']:
                    match = False
                    break
                if self.current_iteration['order_matters'] == "Yes" and current_var['lock_order'] and current_var['order'] != var['order']:
                    match = False
                    break
            if match:
                count += 1
        return count

    def submit_data(self):
        # Update the current iteration with the new values from the inputs
        for var in self.current_iteration['variables']:
            if var['type'] == 'Boolean':
                var['current_value'] = self.variable_inputs[var['name']].currentText() == "True"
            else:
                var['current_value'] = self.convert_to_correct_type(self.variable_inputs[var['name']].currentText(), var['type'])
            var['lock_value'] = self.variable_inputs[f"{var['name']}_lock_value"].currentText() == "True"
            if self.current_iteration['order_matters'] == "Yes":
                var['lock_order'] = self.variable_inputs[f"{var['name']}_lock_order"].currentText() == "True"

        # Update the optimized variable value
        self.current_iteration['optimized_variable']['value'] = float(self.optimized_var_input.text())

        # Save the updated current iteration data to the file
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

        # Call the optimization algorithm to get the next set of variables
        optimizer = HillClimbingOptimization()
        new_params = optimizer.next_parameters(self.filename, self.problem_title)

        # Check if all states are explored
        if new_params == "All possible states explored.":
            QMessageBox.information(self, "Optimization Complete", "All possible states have been explored.")
            
            # Mark the problem as fully explored
            self.current_iteration['fully_explored'] = True
            with open(self.filename, 'w') as file:
                json.dump(self.data, file, indent=4)
            
            # # Update the existing problems tab
            # if hasattr(self.app, 'existing_problems_tab'):
            #     self.app.existing_problems_tab.load_problems()
            self.app.start_problem_definition()
            self.close()
            return

        # Create a new iteration object with the new parameters
        new_iteration = {
            "title": self.current_iteration['title'],
            "description": self.current_iteration['description'],
            "variables": [
                {
                    "name": var['name'],
                    "type": var['type'],
                    "possible_values": var['possible_values'],
                    "current_value": self.convert_to_correct_type(new_params[var['name']], var['type']),
                    "order": var['order'],
                    "lock_order": var['lock_order'],
                    "lock_value": var['lock_value'],
                    "impact_score": var['impact_score'],
                }
                for var in self.current_iteration['variables']
            ],
            "optimized_variable": {
                "name": self.current_iteration['optimized_variable']['name'],
                "value": 0  # Initialize the value to zero for the new iteration
            },
            "optimization_option": self.current_iteration['optimization_option'],
            "algorithm": self.current_iteration['algorithm'],
            "objective": self.current_iteration['objective'],
            "order_matters": self.current_iteration['order_matters'],
            "num_vars_per_state": self.current_iteration['num_vars_per_state'],
            "iteration_count": self.current_iteration['iteration_count'] + 1,
            "calculated_states": self.calculate_possible_states(),
            "fully_explored": False,
        }

        # Append the new iteration to the list of iterations
        self.data.append(new_iteration)

        # Save the updated list back to the file
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

        QMessageBox.information(self, "Data Submitted", "Data has been updated successfully.")
        self.app.start_problem_definition()

    def convert_to_correct_type(self, value, var_type):
        if var_type == 'Boolean':
            return value == 'True' if isinstance(value, str) else bool(value)
        elif var_type == 'Numerical':
            return int(value)
        elif var_type == 'Categorical':
            return str(value)
        return value

    def convert_to_correct_type(self, value, var_type):
        if var_type == 'Boolean':
            return value == 'True' if isinstance(value, str) else bool(value)
        elif var_type == 'Numerical':
            return int(value)
        elif var_type == 'Categorical':
            return str(value)
        return value

