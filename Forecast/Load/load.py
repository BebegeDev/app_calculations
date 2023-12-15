import json

from Interface.interface import InterfaceCallback

interface = InterfaceCallback



class PowerForecast(InterfaceCallback):

    def __init__(self, mqttc):
        self.flag_get_data = None
        self.P_DES_new = 0
        self.Delta_P = 0
        self.load = 0
        self.Load_delta_fact = 0
        self.Load_delta_fact_percent = 0
        self.flag_power_forecast = False
        self.power_forecast = 1
        self.mqttc = mqttc
        self.K_freq_base = -0.1

    async def callback_data(self, topic="mpei/Forecast/Load"):
        self.mqttc.message_callback_add(topic, self.get_data)


    def get_data(self, client, userdata, data):
        try:
            parsed_data = json.loads(data.payload.decode("utf-8", "ignore"))
            self.validate_data(data)
            if self.flag_get_data:
                self.power_forecast = parsed_data
                self.flag_power_forecast = True
            else:
                print("Получены некорректные данные load.")
        except Exception as e:
            print(f"Ошибка при обработке данных: {e}")
            self.flag_get_data = False

    def regulation_load(self, power_fact):

        if self.flag_power_forecast:
            self.Load_delta_fact = -self.power_forecast + power_fact
            self.Load_delta_fact_percent = self.Load_delta_fact / power_fact * 100
            K_freq = abs(self.Load_delta_fact_percent * self.K_freq_base)
            self.Delta_P = self.Load_delta_fact_percent * -K_freq
            self.flag_power_forecast = False
            print('Факт', power_fact)
            print('Прогноз', self.power_forecast)
            print('Отклонение по прогнозу ', self.Delta_P)

    def validate_data(self, data):
        if data:
            self.flag_get_data = True
