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
    optimize.optimize(500, [1, 0, -1, -1, 1, 1])
    optimize.optimize(1000, [-1, -1, -1, 1, 1, 0])
    optimize.optimize_callback()


if __name__ == '__main__':
    main()
