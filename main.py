# импорты нужных модулей и библиотек
import asyncio
from CreateJson.create_json_param_DGU import create_json
from Forecast.DES.power_forecast import PowerForecast as DESPowerForecast
from Forecast.Load.load import PowerForecast as LoadPowerForecast
from Forecast.SES.power_forecast import PowerForecast as SESPowerForecast
from Forecast.SNE.power_forecast import PowerForecast as SNEPowerForecast
from Frequency.frequency import Frequency
from Optimize.optimize import Optimize
from Optimize.optimize_callback import OptimizeCallback
from Connected.contact_mqtt import connection
from utils.create_file_and_path import Util
from utils.publish import Publish
from Connected.connection_db import add_user


async def process_data():
    # Формирование JSON файла с параметрами ДГУ
    create_json()
    # Создание экземпляра класса Util для возможности читать и сохранять данные в файлах разного расширения.
    data_path = Util()
    # Вызов функции для подключения к MQTT и проверки подключения
    mqttc = connection()
    connect = add_user()
    # Создание экземпляра класса Frecency для вызова метода с приемом, передачей и расчетом отклонения частоты.
    freq = Frequency(mqttc)
    # Создание экземпляра класса Optimize() для вызовов методов инициализации оптимизации, оптимизации.
    optimize = Optimize()
    # Создание экземпляра класса OptimizeCallback(mqttc) для получения данных о доступных ДГУ.
    optimize_callback = OptimizeCallback(mqttc)
    # Экземпляры классов для прогнозирования мощности ДЭС, СЭС, СНЭ, нагрузки.
    forecast_dgu = DESPowerForecast(mqttc)
    forecast_ses = SESPowerForecast(mqttc)
    forecast_sne = SNEPowerForecast(mqttc)
    forecast_load = LoadPowerForecast(mqttc)
    # Вызов метода init_optimize() для формирования ресурсов в работе оптимизации.
    optimize.init_optimize(connect)
    # Создание экземпляра класса Publish(mqttc) для возможности публиковать данные.
    publish = Publish(mqttc)

    data_to_add = ['P_DES_new', 'Delta_P', 'frequency', 'Freq_delta_fact', 'P_DGU']
    # Создание списка задач, для запуска их в асинхронном режиме.
    tasks = [freq.callback_data(), forecast_ses.callback_data(), forecast_sne.callback_data(),
             forecast_dgu.callback_data(), forecast_load.callback_data(), optimize_callback.callback_data()]
    # запуск задач в асинхронном режиме
    await asyncio.gather(*tasks)
    # цикл для обработки событий
    while True:
        # проверка на наличие спрогнозированной мощности ДЭС и частоты
        if all(flag.flag_get_data for flag in [freq, forecast_dgu]):
            # метод регулирования частоты
            freq.regulation_frequency()
            # метод регулирования мощности ДЭС
            forecast_load.regulation_load(forecast_dgu.power_forecast)
            # запуск оптимизации по новой целевой мощности
            optimize.optimize(optimize_callback.excluded_engines, 1000)
            # публикация результатов оптимизации
            publish.optimize_publish(optimize)
            # публикация результатов новой частоты
            publish.regulation_frequency(freq, data_path)
            # публикация результатов новой нагрузки
            publish.regulation_load(forecast_load)
        # возврат флагов в изначальное состояние
        for flag in [freq, forecast_dgu, optimize_callback]:
            flag.flag_get_data = False
        # задержка в 1 секунду
        await asyncio.sleep(1)


if __name__ == '__main__':
    # запуск главной функции
    asyncio.run(process_data())
