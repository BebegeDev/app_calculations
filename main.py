import csv

import mqtt.contact_mqtt
import Optimize.optimize
import CreateJson.create_json_param_DGU
from sys import platform
import Frequency.frequency
import DGU.power_forecast
import SES.power_farecast
import SNE.power_forecast
import utils.publish


def main():
    param_dgu = ''
    if platform == 'win32' or platform == 'win64':
        param_dgu = CreateJson.create_json_param_DGU.open_json("\\utils\\param_dgu.json")
    elif platform == 'linux' or platform == 'linux2':
        param_dgu = CreateJson.create_json_param_DGU.open_json("/utils/param_dgu.json")

    mqttc = mqtt.contact_mqtt.connection()

    freq = Frequency.frequency.Frequency(mqttc)
    optimize = Optimize.optimize.Optimize(mqttc)
    forecast_dgu = DGU.power_forecast.PowerForecast(mqttc)
    forecast_ses = SES.power_farecast.PowerForecast(mqttc)
    forecast_sne = SNE.power_forecast.PowerForecast(mqttc)
    optimize.init_optimize(param_dgu)
    publish = utils.publish.Publish(mqttc)
    with open('result.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        data_to_add = ['P_DES_new',
                       'Delta_P',
                       'frequency',
                       'Freq_delta_fact',
                       'P_DGU'
                       ]
        writer.writerow(data_to_add)
    while True:
        freq.callback_data()
        forecast_ses.callback_data()
        forecast_sne.callback_data()
        forecast_dgu.callback_data()
        freq.check_frequency()
        freq.regulation_frequency(forecast_dgu.power_forecast)

        optimize.optimize_callback_excluded_engines()
        optimize.optimize(freq.P_DES_new)
        publish.optimize_publish(optimize)
        publish.regulation_frequency(freq)


if __name__ == '__main__':
    main()
