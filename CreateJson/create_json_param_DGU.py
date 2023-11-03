import json
import os


def create_json(param_dgu=None, output_file=None):
    if param_dgu is None:
        param_dgu = {
            1: [0.94, 100, 400, 217.2],
            2: [0.94, 100, 400, 217.2],
            3: [0.944, 120, 520, 236.5],
            4: [0.944, 120, 520, 236.5],
            5: [0.94, 80, 315, 288],
            6: [0.94, 80, 315, 288],
        }

    if output_file is None:
        output_file = "param_dgu.json"

    script_path = os.path.abspath(__file__)
    project_root_path = os.path.dirname(os.path.dirname(script_path))
    json_file_path = os.path.join(project_root_path, "utils", output_file)

    if os.path.exists(json_file_path):
        print(f"Файл '{json_file_path}' уже существует.")
        return

    with open(json_file_path, "w") as json_file:
        json.dump(param_dgu, json_file)
