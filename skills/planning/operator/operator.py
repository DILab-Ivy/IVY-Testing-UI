import json
from typing import List, Dict


class Operator:
    def __init__(self, name: str, preconditions: List[str], postconditions: List[str]):
        self.name = name
        self.preconditions = preconditions
        self.postconditions = postconditions

    def __repr__(self):
        return f"Operator(name={self.name}, preconditions={self.preconditions}, postconditions={self.postconditions})"


# Function to read operator from a JSON file
def read_operators_from_json(file_path: str) -> Dict[str, Operator]:
    with open(file_path, 'r') as file:
        data = json.load(file)

    operators = {}
    for op_data in data:
        name = op_data['name']
        preconditions = op_data['preconditions']
        postconditions = op_data['postconditions']
        operator = Operator(name, preconditions, postconditions)
        operators[name] = operator

    return operators
