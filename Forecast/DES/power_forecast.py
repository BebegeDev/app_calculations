import json
from Interface.interface import InterfaceCallback

interface = InterfaceCallback


class PowerForecast(InterfaceCallback):

    def __init__(self, mqttc):
        self.flag_get_data = False
        self.flag_power_forecast = False
        self.power_forecast = 0
        self.mqttc = mqttc

    async def callback_data(self, topic="mpei/Forecast/DES"):
        self.mqttc.message_callback_add(topic, self.get_data)

    def get_data(self, client, userdata, data):
        try:
            parsed_data = json.loads(data.payload.decode("utf-8", "ignore"))
            self.validate_data(data)
            if self.flag_get_data:
                self.power_forecast = parsed_data
                self.flag_power_forecast = True
            else:
                print("Получены некорректные данные des.")
        except Exception as e:
            print(f"Ошибка при обработке данных: {e}")
            self.flag_get_data = False


    def validate_data(self, data):
        if data:
            self.flag_get_data = True
            return True


