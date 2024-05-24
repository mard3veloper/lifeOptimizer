import json
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QDoubleValidator
from genetic_algo import GeneticAlgo
from hill_climbing import HillClimbing
from reinforcement_learning import ReinforcementLearning
# from problem_definition import ProblemDefinitionPage

class IterativeOptimizationPage(QMainWindow):
    def __init__(self, main_app, problem_title, filename):
        super().__init__()
        self.main_app = main_app
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
            # Display the title and description from the current iteration
            layout.addWidget(QLabel(f"Optimization for: {self.current_iteration['title']}"))
            layout.addWidget(QLabel(f"Description: {self.current_iteration['description']}"))

            # Dynamically add labels and inputs for each variable
            self.variable_inputs = {}
            for var in self.current_iteration['variables']:
                var_label = QLabel(f"{var['name']}:")
                layout.addWidget(var_label)
                if var.get('type', '') == 'boolean':
                    # Create a toggle button for boolean variables
                    var_button = QPushButton("True" if var['value'] == 'true' else "False")
                    var_button.setCheckable(True)
                    var_button.setChecked(var['value'] == 'true')
                    var_button.clicked.connect(lambda checked, v=var['name'], b=var_button: self.toggle_boolean(v, b))
                    layout.addWidget(var_button)
                    self.variable_inputs[var['name']] = var_button
                else:
                    var_input = QLineEdit(self)
                    var_input.setText(var['value'])
                    layout.addWidget(var_input)
                    self.variable_inputs[var['name']] = var_input

            # Utility measure input with numeric validation
            utility_measure_label = QLabel(f"{self.current_iteration['utility_measure']['name']}:")
            self.utility_measure_input = QLineEdit(self)
            self.utility_measure_input.setText(str(self.current_iteration['utility_measure']['value']))
            self.utility_measure_input.setPlaceholderText("Enter numeric value for utility measure")
            # Applying the numeric validator
            validator = QDoubleValidator()
            validator.setNotation(QDoubleValidator.StandardNotation)
            self.utility_measure_input.setValidator(validator)
            layout.addWidget(utility_measure_label)
            layout.addWidget(self.utility_measure_input)

            # Submit and Done buttons
            submit_button = QPushButton("Submit")
            submit_button.clicked.connect(self.submit_data)
            layout.addWidget(submit_button)

            display_opt_button = QPushButton("Display Current Optimum")
            display_opt_button.clicked.connect(self.display_current_optimum)
            layout.addWidget(display_opt_button)

            done_button = QPushButton("Done")
            done_button.clicked.connect(self.handle_done)
            layout.addWidget(done_button)
        else:
            # If there are no iterations, display a message
            layout.addWidget(QLabel("No data available"))


    def toggle_boolean(self, variable_name, button):
        new_value = 'false' if button.text() == 'True' else 'true'
        button.setText(new_value.capitalize())

    def handle_done(self):
        self.main_app.start_problem_definition()

    def display_current_optimum(self):
        if not self.data:
            QMessageBox.information(self, "No Data", "No optimization data available.")
            return

        # Find the iteration with the highest utility value
        highest_utility_iteration = max(self.data, key=lambda item: item['utility_measure']['value'])

        # Create the message to display
        message = f"Optimum found with Utility Value: {highest_utility_iteration['utility_measure']['value']}\n"
        message += "\nVariables:\n"
        for var in highest_utility_iteration['variables']:
            message += f"{var['name']}: {var['value']}\n"

        # Display the message
        QMessageBox.information(self, "Current Optimum", message)

    def submit_data(self):
        # Find the object with the maximum iteration count
        max_iteration_count = max(item['iteration_count'] for item in self.data)

        # Update the utility value of the object with the maximum iteration count
        for item in self.data:
            if item['iteration_count'] == max_iteration_count:
                item['utility_measure']['value'] = float(self.utility_measure_input.text())

        # Save the updated data to ensure the algorithm sees the latest changes
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

        # call the next_parameters method of the optimization algorithm
        # Instantiate the appropriate algorithm based on the current algorithm setting
        algorithms = {
            'Genetic': GeneticAlgo,
            'Hill Climbing': HillClimbing,
            'Reinforcement Learning': ReinforcementLearning
        }

        algorithm_class = algorithms.get(self.current_iteration['algorithm'])
        if algorithm_class:
            algorithm = algorithm_class()
            new_params = algorithm.next_parameters(self.filename)

            # Update the GUI with new parameters or handle them as needed
            for var_name, new_value in new_params.items():
                if var_name in self.variable_inputs:
                    self.variable_inputs[var_name].setText(new_value)

            # Inform the user
            QMessageBox.information(self, "Algorithm Execution", "Parameters updated based on algorithm output.")
        else:
            QMessageBox.warning(self, "Algorithm Error", "No valid algorithm specified.")

        # Create a new iteration object with incremented iteration count
        new_iteration = {
            "title": self.current_iteration['title'],
            "description": self.current_iteration['description'],
            "utility_measure": {
                "name": self.current_iteration['utility_measure']['name'],
                "value": 0  # Reset utility value to zero for the new iteration
            },
            "algorithm": self.current_iteration['algorithm'],
            "variables": [
                {"name": var['name'], "value": self.variable_inputs[var['name']].text() if not isinstance(self.variable_inputs[var['name']], QPushButton) else ('True' if self.variable_inputs[var['name']].text() == 'True' else 'False')}
                for var in self.current_iteration['variables']
            ],
            "iteration_count": max_iteration_count + 1
        }

        # Append the new iteration to the list of iterations
        self.data.append(new_iteration)

        # Save the updated list back to the file
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

        # Inform the user about the update
        QMessageBox.information(self, "Data Submitted", "Data has been updated successfully.")
