def apply_dark_theme(app):
    with open('app\styling\dark_theme.qss', 'r') as file:
        app.setStyleSheet(file.read())