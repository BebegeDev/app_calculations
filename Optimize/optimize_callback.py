import json
from Interface.interface import InterfaceCallback

interface = InterfaceCallback


class OptimizeCallback(InterfaceCallback):

    def __init__(self, mqttc):
        self.excluded_engines = [1 for _ in range(6)]
        self.flag_get_data = False
        self.flag_power_forecast = False
        self.power_forecast = 0
        self.mqttc = mqttc

    async def callback_data(self, topic="mpei/DES/excluded_engines"):
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
            parsed_data = data.payload.decode()
            excluded_engines = eval(parsed_data)
            self.excluded_engines = [int(x) for x in excluded_engines]
            self.validate_data(data)
            if self.flag_get_data:
                self.power_forecast = parsed_data
            else:
                print("Получены некорректные данные.")
        except Exception as e:
            print(f"Ошибка при обработке данных: {e}")
            self.flag_get_data = False

    def validate_data(self, data):
        """

        :param data: необходимый флаг (временный)
        """
        if data:
            self.flag_get_data = True
            return True
