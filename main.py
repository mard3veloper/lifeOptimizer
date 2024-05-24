import sys
from PyQt5.QtWidgets import QApplication
from problem_definition import ProblemDefinitionPage
from PyQt5.QtGui import QIntValidator, QColor, QPalette
from iterative_optimization import IterativeOptimizationPage

class OptimizationApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.apply_dark_theme()

    def start_problem_definition(self):
        if self.main_window is not None:
            self.main_window.close()
        self.main_window = ProblemDefinitionPage(self)
        self.main_window.show()

    def start_iterative_optimization(self, main_app, problem_title, filename):
        if self.main_window is not None:
            self.main_window.close()
        self.main_window = IterativeOptimizationPage(main_app, problem_title, filename)
        self.main_window.show()

    def start(self):
        self.start_problem_definition()
        sys.exit(self.app.exec_())

    def apply_dark_theme(self):
        # Set a dark theme for the application
        self.app.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #cccccc;
            }
            QLineEdit {
                background-color: #333333;
                border: 1px solid #555555;
                border-radius: 2px;
            }
            QPushButton {
                background-color: #333333;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:disabled {
                background-color: #444444;
                color: #666666;
            }
            QTextEdit {
                background-color: #333333;
                border: none;
            }
            QComboBox {
                background-color: #333333;
                border-radius: 2px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QListWidget {
                background-color: #333333;
                border-radius: 2px;
            }
            QTabWidget::pane {
                border-top: 2px solid #555555;
            }
            QTabBar::tab {
                background: #555555;
                color: #eeeeee;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: #333333;
                color: #ffffff;
            }
            QLabel {
                color: #cccccc;
            }
        """)

if __name__ == "__main__":
    app = OptimizationApp()
    app.start()
