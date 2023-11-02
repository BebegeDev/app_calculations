import json
import os


def create_json():
    param_dgu = {
        1: [0.94, 100, 400, 217.2],
        2: [0.94, 100, 400, 217.2],
        3: [0.944, 120, 520, 236.5],
        4: [0.944, 120, 520, 236.5],
        5: [0.94, 80, 315, 288],
        6: [0.94, 80, 315, 288],
    }

    current_script_path = os.path.abspath(__file__)
    project_root_path = os.path.dirname(os.path.dirname(current_script_path)) + "\\utils\\param_dgu.json"

    with open(project_root_path, "w") as json_file:
        json.dump(param_dgu, json_file)


create_json()
