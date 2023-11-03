import asyncio
from CreateJson.create_json_param_DGU import create_json
from Forecast.DES.power_forecast import PowerForecast
from Forecast.Load.load import PowerForecast as LoadPowerForecast
from Forecast.SES.power_forecast import PowerForecast as SESPowerForecast
from Forecast.SNE.power_forecast import PowerForecast as SNEPowerForecast
from Frequency.frequency import Frequency
from Optimize.optimize import Optimize
from Optimize.optimize_callback import OptimizeCallback
from mqtt.contact_mqtt import connection
from utils.create_file_and_path import Util
from utils.publish import Publish


async def process_data():
    create_json()
    data_path = Util()
    mqttc = connection()

    freq = Frequency(mqttc)
    optimize = Optimize()
    optimize_callback = OptimizeCallback(mqttc)
    forecast_dgu = PowerForecast(mqttc)
    forecast_ses = SESPowerForecast(mqttc)
    forecast_sne = SNEPowerForecast(mqttc)
    forecast_load = LoadPowerForecast(mqttc)
    optimize.init_optimize(data_path.open_json("param_dgu.json"))
    publish = Publish(mqttc)

    data_to_add = ['P_DES_new', 'Delta_P', 'frequency', 'Freq_delta_fact', 'P_DGU']

    tasks = [freq.callback_data(), forecast_ses.callback_data(), forecast_sne.callback_data(),
             forecast_dgu.callback_data(), forecast_load.callback_data(), optimize_callback.callback_data()]

    await asyncio.gather(*tasks)

    while True:
        await asyncio.sleep(1)
        if all(flag.flag_get_data for flag in [freq, forecast_ses, forecast_dgu, forecast_sne, forecast_load]):
            freq.regulation_frequency()
            forecast_load.regulation_load(forecast_dgu.power_forecast)
            optimize.optimize(optimize_callback.excluded_engines,
                              sum([forecast_dgu.power_forecast,
                                  freq.Delta_P,
                                  forecast_load.Delta_P]))
            publish.optimize_publish(optimize)
            publish.regulation_frequency(freq, data_path)
            publish.regulation_load(forecast_load)

        for flag in [freq, forecast_ses, forecast_dgu, forecast_sne, forecast_load, optimize_callback]:
            flag.flag_get_data = False


if __name__ == '__main__':
    asyncio.run(process_data())
