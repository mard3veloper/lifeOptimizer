import os

def validate_numeric_input(min_val, max_val):
    return min_val.isdigit() and max_val.isdigit() and int(min_val) < int(max_val)

def validate_title(title):
    filename = os.path.join("resources/problems", f"{title.replace(' ', '_')}.json")
    return not os.path.exists(filename)
