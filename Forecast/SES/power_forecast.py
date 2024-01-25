import json
from Interface.interface import InterfaceCallback

interface = InterfaceCallback


class PowerForecast(InterfaceCallback):
    """

    Класс предназначен для расчета и обработки прогноза и публикации значений.
    :callback_data --> асинхронная функция приема значений по-заданному топику.
    :get_data --> метод паркинга и проверки данных.
    """

    def __init__(self, mqttc):
        self.flag_get_data = False
        self.flag_power_forecast = False
        self.power_forecast = 0
        self.mqttc = mqttc

    async def callback_data(self, topic="mpei/Forecast/SES"):
        """

        :param topic: топик для подписки
        """
        self.mqttc.message_callback_add(topic, self.get_data)

    def get_data(self, client, userdata, data):
        """

        :param client: клиент mqtt
        :param userdata: дата от клиента
        :param data: полезная нагрузка
        """
        try:
            parsed_data = json.loads(data.payload.decode("utf-8", "ignore"))
            self.validate_data(data)
            if self.flag_get_data:
                self.power_forecast = parsed_data
                self.flag_power_forecast = True
                self.flag_get_data = True
            else:
                print("Получены некорректные данные ses.")
        except Exception as e:
            print(f"Ошибка при обработке данных: {e}")
            self.flag_get_data = False

    def validate_data(self, data):
        """

        :param data: необходимый флаг (временный)
        """
        if data:
            self.flag_get_data = True
