import sys
import os
from PyQt5.QtWidgets import QApplication
from .problem_definition import ProblemDefinitionPage
from .iterative_optimization import IterativeOptimizationPage
from .style import apply_dark_theme

class OptimizationApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None
        apply_dark_theme(self.app)

    def start_problem_definition(self):
        if self.main_window is not None:
            self.main_window.close()
        self.main_window = ProblemDefinitionPage(self)
        self.main_window.show()

    def start_iterative_optimization(self, problem_title, filename):
        if self.main_window is not None:
            self.main_window.close()
        self.main_window = IterativeOptimizationPage(self, problem_title, filename)
        self.main_window.show()

    def start(self):
        self.start_problem_definition()
        sys.exit(self.app.exec_())
