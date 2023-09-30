import time

import mqtt.contact_mqtt
import Optimize.optimize
import CreateJson.create_json_param_DGU
from sys import platform


def main():
    param_dgu = ''
    if platform == 'win32' or platform == 'win64':
        param_dgu = CreateJson.create_json_param_DGU.open_json("\\utils\\param_dgu.json")
    elif platform == 'linux' or platform == 'linux2':
        param_dgu = CreateJson.create_json_param_DGU.open_json("/utils/param_dgu.json")
    mqttc = mqtt.contact_mqtt.connection()
    optimize = Optimize.optimize.Optimize(mqttc)
    optimize.init_optimize(param_dgu)
    import csv
    with open('file.csv', mode='a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        data_to_add = ['Moment',
                       'Rotation_speed',
                       'Changing_network_frequency',
                       'Changing_network_frequency_deviation',
                       'Speed_deviation']
        writer.writerow(data_to_add)

    while True:

        optimize.optimize_callback_load()
        optimize.optimize_callback_excluded_engines()
        optimize.optimize()
        optimize.optimize_publish()


if __name__ == '__main__':
    main()
