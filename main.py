import asyncio
import csv
from sys import platform
import CreateJson.create_json_param_DGU
import Forecast.DES.power_forecast
import Forecast.Load.load
import Forecast.SES.power_farecast
import Forecast.SNE.power_forecast
import Frequency.frequency
import Optimize.optimize
import mqtt.contact_mqtt
import utils.create_data_file
import utils.publish


async def main():
    CreateJson.create_json_param_DGU.create_json()
    data_path = utils.create_data_file.Util()
    mqttc = mqtt.contact_mqtt.connection()

    freq = Frequency.frequency.Frequency(mqttc)
    optimize = Optimize.optimize.Optimize()
    forecast_dgu = Forecast.DES.power_forecast.PowerForecast(mqttc)
    forecast_ses = Forecast.SES.power_farecast.PowerForecast(mqttc)
    forecast_sne = Forecast.SNE.power_forecast.PowerForecast(mqttc)
    forecast_load = Forecast.Load.load.PowerForecast(mqttc)
    optimize.init_optimize(data_path.open_json("param_dgu.json"))
    publish = utils.publish.Publish(mqttc)
    data_to_add = ['P_DES_new',
                   'Delta_P',
                   'frequency',
                   'Freq_delta_fact',
                   'P_DGU'
                   ]
    data_path.open_csv('result.csv', mode='w', name_column=data_to_add)


    tasks = [freq.callback_data(),
             forecast_ses.callback_data(),
             forecast_sne.callback_data(),
             forecast_dgu.callback_data(),
             forecast_load.callback_data(),
             optimize.optimize_callback_power(mqttc),
             optimize.optimize_callback_excluded_engines(mqttc)
             ]

    await asyncio.gather(*tasks)
    while True:
        if freq.flag_get_data and \
                forecast_ses.flag_get_data and \
                forecast_dgu.flag_get_data and \
                forecast_sne.flag_get_data and \
                forecast_load.flag_get_data:

            freq.regulation_frequency(forecast_dgu.power_forecast)
            forecast_load.regulation_load(forecast_dgu.power_forecast)
            optimize.optimize(freq.P_DES_new)
            publish.optimize_publish(optimize)
            publish.regulation_frequency(freq, data_path)
            publish.regulation_load(forecast_load)

            freq.flag_get_data = False
            forecast_ses.flag_get_data = False
            forecast_dgu.flag_get_data = False
            forecast_sne.flag_get_data = False
            forecast_load.flag_get_data = False


if __name__ == '__main__':
    asyncio.run(main())
