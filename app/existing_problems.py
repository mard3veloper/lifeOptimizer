import os
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QLabel, QMessageBox)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

class ExistingProblemsTab(QWidget):
    
    problem_selected = pyqtSignal(str)  # Define a signal to emit the filename

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.problem_list = QListWidget()
        layout.addWidget(self.problem_list)

        self.load_problems()

    def load_problems(self):
        # Clear the existing list
        self.problem_list.clear()

        problems_dir = os.path.join(os.path.dirname(__file__), '../problems')
        if not os.path.exists(problems_dir):
            os.makedirs(problems_dir)

        for filename in os.listdir(problems_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(problems_dir, filename)
                with open(filepath, 'r') as file:
                    problem_data = json.load(file)
                    if problem_data:
                        problem_title = problem_data[-1]['title']
                        self.add_problem_item(problem_title, filepath)

    def add_problem_item(self, title, filepath):
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        item_layout.addWidget(title_label)

        current_state_button = QPushButton("Current State")
        current_state_button.clicked.connect(lambda: self.view_current_state(filepath))
        item_layout.addWidget(current_state_button)

        edit_button = QPushButton("Edit Problem")
        edit_button.clicked.connect(lambda: self.edit_problem(filepath))
        item_layout.addWidget(edit_button)

        best_state_button = QPushButton("Display Current Best State")
        best_state_button.clicked.connect(lambda: self.display_best_state(filepath))
        item_layout.addWidget(best_state_button)

        history_button = QPushButton("History")
        history_button.clicked.connect(lambda: self.view_history(filepath))
        item_layout.addWidget(history_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_problem(filepath, item_widget))
        item_layout.addWidget(delete_button)

        item = QListWidgetItem()
        item.setSizeHint(item_widget.sizeHint())

        self.problem_list.addItem(item)
        self.problem_list.setItemWidget(item, item_widget)

    def view_current_state(self, filepath):
        # Add logic to view the current state
        self.problem_selected.emit(filepath)

    def edit_problem(self, filepath):
        # Add logic to edit the problem
        QMessageBox.information(self, "Edit Problem", f"Editing problem {filepath}")

    def display_best_state(self, filepath):
        # Add logic to display the current best state
        QMessageBox.information(self, "Best State", f"Displaying best state of {filepath}")

    def view_history(self, filepath):
        # Add logic to view the history
        QMessageBox.information(self, "History", f"Viewing history of {filepath}")

    def delete_problem(self, filepath, item_widget):
            reply = QMessageBox.question(self, "Delete Problem", "Are you sure you want to delete this problem?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                os.remove(filepath)
                # Find the corresponding QListWidgetItem
                for index in range(self.problem_list.count()):
                    item = self.problem_list.item(index)
                    if self.problem_list.itemWidget(item) == item_widget:
                        self.problem_list.takeItem(index)
                        item_widget.deleteLater()
                        break
