import csv
import json
import os
from sys import platform


class Util:

    @staticmethod
    def __get_data_path(name_file):
        if platform == 'win32' or platform == 'win64':
            return f"\\utils\\{name_file}"
        elif platform == 'linux' or platform == 'linux2':
            return f"/utils/{name_file}"


    def open_json(self, name_file):
        try:
            current_script_path = os.path.abspath(__file__)
            path = self.__get_data_path(name_file)
            project_root_path = os.path.dirname(os.path.dirname(current_script_path)) + path
            with open(project_root_path, 'r') as json_file:
                data = json.load(json_file)
            return data
        except Exception as e:
            print(f"Ошибка открытия {name_file}: {e}")

    def create_json(self, name_file, data):
        try:
            current_script_path = os.path.abspath(__file__)
            path = self.__get_data_path(name_file)
            project_root_path = os.path.dirname(os.path.dirname(current_script_path)) + path
            with open(project_root_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
        except Exception as e:
            print(f"Ошибка создания {name_file}: {e}")

    def open_csv(self, name_file, mode, name_column):
        current_script_path = os.path.abspath(__file__)
        path = self.__get_data_path(name_file)
        project_root_path = os.path.dirname(os.path.dirname(current_script_path)) + path
        with open(project_root_path, mode=mode, encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            data_to_add = name_column
            writer.writerow(data_to_add)
