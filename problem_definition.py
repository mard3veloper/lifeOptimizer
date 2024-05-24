import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QFormLayout, QComboBox, QListWidget, QMessageBox, QTabWidget, QListWidgetItem, QInputDialog, QSpinBox)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, QTimer

class ProblemDefinitionPage(QMainWindow):
    def __init__(self, main_app):
        super().__init__()
        self.setWindowTitle("Problem Definition")
        self.setGeometry(100, 100, 800, 600)
        self.variables = []
        self.initUI()

    def initUI(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        create_problem_widget = QWidget()
        create_problem_layout = QVBoxLayout()
        create_problem_widget.setLayout(create_problem_layout)
        self.setup_problem_definition_tab(create_problem_layout)

        list_problems_widget = QWidget()
        list_problems_layout = QVBoxLayout()
        list_problems_widget.setLayout(list_problems_layout)
        self.problem_list = QListWidget()
        list_problems_layout.addWidget(self.problem_list)

        self.tabs.addTab(create_problem_widget, "Define Problem")
        self.tabs.addTab(list_problems_widget, "Existing Problems")

    def setup_problem_definition_tab(self, layout):
        # Problem Title and Description
        title_layout = QFormLayout()
        self.title_entry = QLineEdit()
        title_layout.addRow(QLabel("Problem Title:"), self.title_entry)
        self.title_error_label = QLabel("")
        self.title_error_label.setStyleSheet("color: red;")
        self.title_error_label.setVisible(False)
        title_layout.addRow(self.title_error_label)
        self.title_entry.textChanged.connect(self.validate_title)  # Connect title entry to validation method
        layout.addLayout(title_layout)

        desc_layout = QFormLayout()
        self.desc_text_edit = QTextEdit()
        desc_layout.addRow(QLabel("Problem Description:"), self.desc_text_edit)
        layout.addLayout(desc_layout)

        # Initialize variable display layout
        self.variable_display_layout = QVBoxLayout()
        layout.addLayout(self.variable_display_layout)

        # Layout for adding variables
        var_layout = QHBoxLayout()
        var_layout.addWidget(QLabel("Variable Name:"))
        self.variable_entry = QLineEdit()
        var_layout.addWidget(self.variable_entry)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Select Type", "Boolean", "Numerical", "Categorical"])
        var_layout.addWidget(QLabel("Type:"))
        var_layout.addWidget(self.type_combo)

        self.min_label = QLabel("Min (whole number):")
        self.min_value_entry = QLineEdit()
        self.min_value_entry.setValidator(QIntValidator())
        self.max_label = QLabel("Max (whole number):")
        self.max_value_entry = QLineEdit()
        self.max_value_entry.setValidator(QIntValidator())
        var_layout.addWidget(self.min_label)
        var_layout.addWidget(self.min_value_entry)
        var_layout.addWidget(self.max_label)
        var_layout.addWidget(self.max_value_entry)

        cat_layout = QVBoxLayout()
        self.categories_label = QLabel("Added Categories:")
        self.categories_list = QListWidget()
        self.categories_list.setVisible(False)  # Initially hidden
        cat_layout.addWidget(self.categories_label)
        cat_layout.addWidget(self.categories_list)
        self.categories_label.setVisible(False)  # Initially hidden
        self.categories_entry = QLineEdit()
        self.add_category_button = QPushButton("Add Category")
        self.add_category_button.clicked.connect(self.add_category)
        cat_sub_layout = QHBoxLayout()
        cat_sub_layout.addWidget(self.categories_entry)
        cat_sub_layout.addWidget(self.add_category_button)
        cat_layout.addLayout(cat_sub_layout)
        var_layout.addLayout(cat_layout)



        self.add_variable_button = QPushButton("Add Variable")
        self.add_variable_button.clicked.connect(self.add_variable)
        self.add_variable_button.setEnabled(False)  # Start with the button disabled
        var_layout.addWidget(self.add_variable_button)

        self.update_variable_type_ui()

        layout.addLayout(var_layout)

        # Optimized Variable Entry
        optimized_var_layout = QHBoxLayout()
        optimized_var_layout.addWidget(QLabel("Optimized Variable Name:"))
        self.optimized_variable_entry = QLineEdit()
        optimized_var_layout.addWidget(self.optimized_variable_entry)
        layout.addLayout(optimized_var_layout)

        # Optimization Options
        optimization_options_layout = QHBoxLayout()
        self.optimization_option_combo = QComboBox()
        self.optimization_option_combo.addItems(["Select Optimization Type", "Automatic Optimization", "Manual Optimization"])
        optimization_options_layout.addWidget(QLabel("Optimization Options:"))
        optimization_options_layout.addWidget(self.optimization_option_combo)
        layout.addLayout(optimization_options_layout)

        # Algorithm Selection and Objective Function Setup
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Select an Algorithm", "Genetic", "Hill Climbing", "Reinforcement Learning", "Test Every Combination"])
        self.objective_function_combo = QComboBox()
        self.objective_function_combo.addItems(["Maximize", "Minimize"])
        
        self.algorithm_label = QLabel("Select Algorithm:")
        self.objective_label = QLabel("Objective:")

        self.algorithm_layout = QHBoxLayout()
        self.algorithm_layout.addWidget(self.algorithm_label)
        self.algorithm_layout.addWidget(self.algorithm_combo)
        self.algorithm_layout.addWidget(self.objective_label)
        self.algorithm_layout.addWidget(self.objective_function_combo)

        layout.addLayout(self.algorithm_layout)

        # Initially hide algorithm selection and objective function
        self.hide_algorithm_options()

        # Optimization Options setup
        self.optimization_option_combo.currentIndexChanged.connect(self.update_optimization_ui)

        # Add 'Order Matters' Checkbox
        self.order_matters_combo = QComboBox()
        self.order_matters_combo.addItems(["No", "Yes"])
        order_matters_layout = QHBoxLayout()
        order_matters_layout.addWidget(QLabel("Does the order of variables matter?"))
        order_matters_layout.addWidget(self.order_matters_combo)
        layout.addLayout(order_matters_layout)

        # Add 'Number of Variables per State' Entry
        self.num_vars_per_state_spinbox = QSpinBox()
        self.num_vars_per_state_spinbox.setRange(1, 100)  # Assuming a max of 100 variables
        self.num_vars_per_state_spinbox.setValue(len(self.variables))  # Default to total number of variables
        self.num_vars_per_state_spinbox.valueChanged.connect(self.update_possible_states)
        num_vars_layout = QHBoxLayout()
        num_vars_layout.addWidget(QLabel("Number of variables per state:"))
        num_vars_layout.addWidget(self.num_vars_per_state_spinbox)
        layout.addLayout(num_vars_layout)

        # Connect signals for recalculating possible states
        self.order_matters_combo.currentIndexChanged.connect(self.update_possible_states)
        self.num_vars_per_state_spinbox.textChanged.connect(self.update_possible_states)

        # Label and box for displaying the number of possible states
        self.states_label = QLabel("Number of Possible States: 0")
        self.states_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.states_label)

        # Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setEnabled(False)
        layout.addWidget(self.submit_button)
        # self.submit_button.clicked.connect(self.submit_data)
        self.submit_button.clicked.connect(self.gather_data)

        self.success_message_label = QLabel("")
        self.success_message_label.setStyleSheet("color: green;")
        self.success_message_label.setVisible(False)
        layout.addWidget(self.success_message_label)

        # Connect signals for validating inputs
        self.categories_list.itemChanged.connect(self.on_category_changed)
        self.categories_list.itemChanged.connect(self.validate_variable_inputs)
        self.title_entry.textChanged.connect(self.validate_inputs)
        self.title_entry.textChanged.connect(self.validate_title)
        self.optimized_variable_entry.textChanged.connect(self.validate_inputs)
        self.optimization_option_combo.currentIndexChanged.connect(self.validate_inputs)
        self.algorithm_combo.currentIndexChanged.connect(self.validate_inputs)
        self.type_combo.currentIndexChanged.connect(self.update_variable_type_ui)
        self.type_combo.currentIndexChanged.connect(self.validate_variable_inputs)
        self.variable_entry.textChanged.connect(self.validate_variable_inputs)
        self.min_value_entry.textChanged.connect(self.validate_variable_inputs)
        self.max_value_entry.textChanged.connect(self.validate_variable_inputs)
        self.categories_list.model().rowsInserted.connect(self.validate_variable_inputs)
        self.categories_list.model().rowsRemoved.connect(self.validate_variable_inputs)

    def update_possible_states(self):
        import math
        from itertools import combinations

        num_vars = self.num_vars_per_state_spinbox.value()  # Get the value from the QSpinBox
        if num_vars > len(self.variables):
            num_vars = len(self.variables)
        self.num_vars_per_state_spinbox.setValue(num_vars)  # Update the QSpinBox value if necessary

        if num_vars <= 0 or not self.variables:
            self.states_label.setText("Number of Possible States: 0")
            return

        total_states = 0
        # Calculate states considering combinations of variables up to the specified number per state
        for variable_combination in combinations(self.variables, num_vars):
            # Calculate the product of possible values for each combination
            states_for_combination = 1
            for var in variable_combination:
                states_for_combination *= len(var['possible_values'])
            
            # If the order of variables matters, multiply by factorial of num_vars
            if self.order_matters_combo.currentText() == "Yes":
                states_for_combination *= math.factorial(num_vars)

            total_states += states_for_combination

        self.states_label.setText(f"Number of Possible States: {total_states}")


    def on_category_changed(self, item):
        # This method is called whenever a list item is edited
        return

    def update_optimization_ui(self):
        # Show or hide Algorithm and Objective based on selected optimization type
        if self.optimization_option_combo.currentText() == "Automatic Optimization":
            self.show_algorithm_options()
        else:
            self.hide_algorithm_options()
        self.validate_inputs()

    def hide_algorithm_options(self):
        # Hide each widget individually
        self.algorithm_label.setVisible(False)
        self.algorithm_combo.setVisible(False)
        self.objective_label.setVisible(False)
        self.objective_function_combo.setVisible(False)

    def show_algorithm_options(self):
        # Show each widget individually
        self.algorithm_label.setVisible(True)
        self.algorithm_combo.setVisible(True)
        self.objective_label.setVisible(True)
        self.objective_function_combo.setVisible(True)

    def update_optimization_ui(self):
        # Check the selected option and update UI accordingly
        if self.optimization_option_combo.currentText() == "Automatic Optimization":
            self.show_algorithm_options()
        else:
            self.hide_algorithm_options()

    def add_category(self):
        category = self.categories_entry.text().strip()
        if category and not any(category == self.categories_list.item(i).text() for i in range(self.categories_list.count())):
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)

            category_label = QLabel(category)
            item_layout.addWidget(category_label)

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda: self.edit_category(category_label))
            item_layout.addWidget(edit_button)

            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda: self.delete_category(item_widget, category))
            item_layout.addWidget(delete_button)

            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())

            self.categories_list.addItem(item)
            self.categories_list.setItemWidget(item, item_widget)
            self.categories_list.setVisible(True)  # Ensure the list is visible
            self.categories_label.setVisible(True)  # Ensure the label is visible
            self.categories_entry.clear()
            self.validate_inputs()

    def edit_category(self, label):
        current_text = label.text()
        new_text, ok = QInputDialog.getText(self, "Edit Category", "Category Name:", QLineEdit.Normal, current_text)
        if ok and new_text.strip():
            label.setText(new_text.strip())
            self.validate_variable_inputs()
            self.validate_inputs()

    def delete_category(self, item_widget, category):
        for i in range(self.categories_list.count()):
            item = self.categories_list.item(i)
            if self.categories_list.itemWidget(item) == item_widget:
                self.categories_list.takeItem(i)
                item_widget.deleteLater()
                break
        self.validate_variable_inputs()
        self.validate_inputs()

    def resize_categories_list(self):
        max_visible_items = 5  # Adjust this to set maximum visible items without scrolling
        row_height = self.categories_list.sizeHintForRow(0)
        if row_height > 0:
            visible_items = min(self.categories_list.count(), max_visible_items)
            self.categories_list.setMaximumHeight(row_height * visible_items + 2 * self.categories_list.frameWidth())

    def update_variable_type_ui(self):
        var_type = self.type_combo.currentText()
        is_numeric = var_type == "Numerical"
        is_categorical = var_type == "Categorical"
        self.min_label.setVisible(is_numeric)
        self.min_value_entry.setVisible(is_numeric)
        self.max_label.setVisible(is_numeric)
        self.max_value_entry.setVisible(is_numeric)
        self.categories_label.setVisible(is_categorical and self.categories_list.count() > 0)
        self.categories_entry.setVisible(is_categorical)
        self.add_category_button.setVisible(is_categorical)
        self.categories_list.setVisible(is_categorical and self.categories_list.count() > 0)

    def add_variable(self):
        var_name = self.variable_entry.text().strip()
        var_type = self.type_combo.currentText()
        if var_name and var_type != "Select Type" and self.validate_numeric_input():
            order = len(self.variables) + 1 if self.order_matters_combo.currentText() == "Yes" else 0
            categories = [self.categories_list.itemWidget(self.categories_list.item(i)).layout().itemAt(0).widget().text() for i in range(self.categories_list.count())] if var_type == "Categorical" else []
            possible_values = categories if var_type == "Categorical" else ([True, False] if var_type == "Boolean" else list(range(int(self.min_value_entry.text()), int(self.max_value_entry.text()) + 1)))
            initial_value = categories[0] if categories else True if var_type == "Boolean" else int(self.min_value_entry.text())
            variable_details = {
                "name": var_name,
                "type": var_type,
                "possible_values": possible_values,
                "current_value": initial_value,
                "order": order,
                "lock_order": False,
                "lock_value": False
            }
            self.variables.append(variable_details)
            self.display_variable(variable_details)
            self.validate_inputs()
            self.clear_variable_inputs()
            self.num_vars_per_state_spinbox.setRange(1, len(self.variables))  # Update range of variables per state
            self.num_vars_per_state_spinbox.setValue(len(self.variables))  # Default to total number of variables
            self.update_possible_states()
            
    def validate_numeric_input(self):
        if self.type_combo.currentText() == "Numerical":
            min_val = self.min_value_entry.text()
            max_val = self.max_value_entry.text()
            if min_val.isdigit() and max_val.isdigit() and int(min_val) < int(max_val):
                return True
            QMessageBox.warning(self, "Input Error", "Minimum value must be less than maximum value and both must be whole numbers.")
            return False
        return True

    def display_variable(self, variable_details):
        display_widget = QWidget()
        display_layout = QHBoxLayout(display_widget)
        display_layout.addWidget(QLabel(variable_details['name']))

        value_combo = QComboBox()
        for value in variable_details['possible_values']:
            value_combo.addItem(str(value))
        value_combo.setCurrentText(str(variable_details['current_value']))
        value_combo.currentTextChanged.connect(lambda value, var=variable_details: self.update_initial_value(var, value))
        display_layout.addWidget(value_combo)

        # Add Edit Button
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda: self.edit_variable(variable_details, display_widget))
        display_layout.addWidget(edit_button)

        # Add Delete Button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_variable(variable_details, display_widget))
        display_layout.addWidget(delete_button)

        self.variable_display_layout.addWidget(display_widget)

    def edit_variable(self, variable_details, widget):
        # Load variable details back to input fields
        self.variable_entry.setText(variable_details['name'])
        self.type_combo.setCurrentText(variable_details['type'])
        if variable_details['type'] == "Numerical":
            self.min_value_entry.setText(str(min(variable_details['possible_values'])))
            self.max_value_entry.setText(str(max(variable_details['possible_values'])))
        elif variable_details['type'] == "Categorical":
            self.categories_list.clear()
            for category in variable_details['possible_values']:
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(0, 0, 0, 0)

                category_label = QLabel(category)
                item_layout.addWidget(category_label)

                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda: self.edit_category(category_label))
                item_layout.addWidget(edit_button)

                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda: self.delete_category(item_widget, category))
                item_layout.addWidget(delete_button)

                item = QListWidgetItem()
                item.setSizeHint(item_widget.sizeHint())

                self.categories_list.addItem(item)
                self.categories_list.setItemWidget(item, item_widget)

            self.categories_list.setVisible(True)
            self.categories_label.setVisible(True)

        self.toggle_widget_visibility(widget, False)  # Hide the widget during editing

        # Add functionality to update the existing variable
        self.add_variable_button.disconnect()
        self.add_variable_button.clicked.connect(lambda: self.update_variable(variable_details, widget))
        self.add_variable_button.setText("Update Variable")
        self.validate_inputs()

    def update_variable(self, variable_details, widget):
        var_name = self.variable_entry.text().strip()
        var_type = self.type_combo.currentText()
        
        # Check if type has changed and adjust possible_values and current_value accordingly
        if var_type == "Boolean":
            possible_values = [True, False]
            current_value = True
        elif var_type == "Numerical":
            min_val = int(self.min_value_entry.text())
            max_val = int(self.max_value_entry.text())
            possible_values = list(range(min_val, max_val + 1))
            current_value = min_val
        elif var_type == "Categorical":
            categories = [self.categories_list.itemWidget(self.categories_list.item(i)).layout().itemAt(0).widget().text() for i in range(self.categories_list.count())]
            possible_values = categories
            current_value = categories[0] if categories else None

        # Update the existing variable details
        variable_details['name'] = var_name
        variable_details['type'] = var_type
        variable_details['possible_values'] = possible_values
        variable_details['current_value'] = current_value

        # Remove the old display widget and clear the layout
        self.variable_display_layout.removeWidget(widget)
        self.num_vars_per_state_spinbox.setValue(len(self.variables))  # Update number of variables per state to new total

        widget.deleteLater()

        # Redisplay all variables to ensure UI consistency
        self.redisplay_all_variables()

        # Restore the button to original "Add Variable" functionality
        self.add_variable_button.setText("Add Variable")
        self.add_variable_button.disconnect()
        self.add_variable_button.clicked.connect(self.add_variable)

        self.clear_variable_inputs()  # Clear the input fields
        self.update_possible_states()  # Update the possible states count
        self.validate_inputs()  # Revalidate all inputs

    def redisplay_all_variables(self):
        # Clear the current display
        while self.variable_display_layout.count():
            child = self.variable_display_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Redisplay all variables
        for var in self.variables:
            self.display_variable(var)

    def toggle_widget_visibility(self, widget, visible=True):
        widget.setVisible(visible)

    def validate_title(self):
        title = self.title_entry.text().strip()
        filename = os.path.join("problems", f"{title.replace(' ', '_')}.json")
        if os.path.exists(filename):
            self.title_error_label.setText("Title already used. Please choose a different title.")
            self.title_error_label.setVisible(True)
            return False
        self.title_error_label.setVisible(False)
        return True


    def gather_data(self):
        problem_data = {
            "title": self.title_entry.text().strip(),
            "description": self.desc_text_edit.toPlainText().strip(),
            "variables": self.variables,
            "optimized_variable": {
                "name": self.optimized_variable_entry.text().strip(),
                "value": 0  # Initialize the value to zero
            },
            "optimization_option": self.optimization_option_combo.currentText(),
            "algorithm": self.algorithm_combo.currentText() if self.optimization_option_combo.currentText() == "Automatic Optimization" else None,
            "objective": self.objective_function_combo.currentText() if self.optimization_option_combo.currentText() == "Automatic Optimization" else None,
            "order_matters": self.order_matters_combo.currentText(),
            "num_vars_per_state": self.num_vars_per_state_spinbox.value(),
            "iteration_count": 0,  # Initialize iteration count to zero
            "calculated_states": self.states_label.text().split(": ")[1]  # Extract the number of possible states
        }
        
        # Create the problems directory if it doesn't exist
        if not os.path.exists("problems"):
            os.makedirs("problems")
        
        # Define the filename
        title = problem_data["title"].replace(" ", "_")  # Replace spaces with underscores for the filename
        filename = os.path.join("problems", f"{title}.json")
        
        # Load existing data if the file exists, otherwise start with an empty list
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
        else:
            data = []
        
        # Append the new problem data
        data.append(problem_data)
        
        # Save the updated list back to the file
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        self.clear_form()  # Clear the form after submission
        print(f"Data saved to {filename}")
        self.success_message_label.setText("Problem Added to Problems Library")
        self.success_message_label.setVisible(True)

        # Hide the success message after 5 seconds
        QTimer.singleShot(5000, self.hide_success_message)

    def delete_variable(self, variable_details, widget):
        self.variables.remove(variable_details)
        widget.setParent(None)
        # Update order of remaining variables
        if self.order_matters_combo.currentText() == "Yes":
            for index, variable in enumerate(self.variables):
                variable['order'] = index + 1
        self.num_vars_per_state_spinbox.setValue(len(self.variables))  # Update number of variables per state to new total
        self.update_possible_states()
        self.validate_inputs()

    def update_initial_value(self, variable_details, value):
        variable_details['current_value'] = type(variable_details['possible_values'][0])(value)
        self.update_possible_states()

    def clear_variable_inputs(self):
        self.variable_entry.clear()
        self.type_combo.setCurrentIndex(0)
        self.min_value_entry.clear()
        self.max_value_entry.clear()
        self.categories_list.clear()
        self.add_variable_button.setText("Add Variable")
        self.add_variable_button.disconnect()
        self.add_variable_button.clicked.connect(self.add_variable)
        self.update_possible_states()
        self.validate_inputs()

    def clear_form(self):
        self.title_entry.clear()
        self.desc_text_edit.clear()
        self.variable_entry.clear()
        self.type_combo.setCurrentIndex(0)
        self.min_value_entry.clear()
        self.max_value_entry.clear()
        self.categories_list.clear()
        self.optimized_variable_entry.clear()
        self.optimization_option_combo.setCurrentIndex(0)
        self.algorithm_combo.setCurrentIndex(0)
        self.objective_function_combo.setCurrentIndex(0)
        self.order_matters_combo.setCurrentIndex(0)
        self.num_vars_per_state_spinbox.setValue(1)
        self.states_label.setText("Number of Possible States: 0")
        self.variables = []
        while self.variable_display_layout.count():
            child = self.variable_display_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.validate_inputs()  # Revalidate the inputs to disable the submit button

    def hide_success_message(self):
        self.success_message_label.setVisible(False)


    def validate_variable_inputs(self):
        var_name = self.variable_entry.text().strip()
        var_type = self.type_combo.currentText()

        if var_type == "Boolean":
            is_valid = bool(var_name and var_type != "Select Type")
        elif var_type == "Numerical":
            min_val = self.min_value_entry.text()
            max_val = self.max_value_entry.text()
            is_valid = bool(var_name and min_val.isdigit() and max_val.isdigit() and int(min_val) < int(max_val))
        elif var_type == "Categorical":
            is_valid = bool(var_name and self.categories_list.count() > 0)
        else:
            is_valid = False

        self.add_variable_button.setEnabled(is_valid)

    def validate_inputs(self):
        title_filled = self.title_entry.text().strip() != "" and self.validate_title()
        has_variables = len(self.variables) > 0
        optimized_var_filled = self.optimized_variable_entry.text().strip() != ""
        optimization_selected = self.optimization_option_combo.currentIndex() != 0

        if self.optimization_option_combo.currentText() == "Automatic Optimization":
            algorithm_selected = self.algorithm_combo.currentIndex() != 0
            all_conditions_met = title_filled and has_variables and optimized_var_filled and optimization_selected and algorithm_selected
        else:
            all_conditions_met = title_filled and has_variables and optimized_var_filled and optimization_selected

        self.submit_button.setEnabled(all_conditions_met)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     ex = ProblemDefinitionPage(None)
#     ex.show()
#     sys.exit(app.exec_())
