import json

import Interface.interface

interface = Interface.interface


class PowerForecast(interface.InterfaceForecast):

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
        self.K_freq_base = -0.5

    async def callback_data(self, topic="mpei/Forecast/Load"):
        self.mqttc.message_callback_add(topic, self.get_data)

    def get_data(self, client, userdata, data):
        self.power_forecast = json.loads(data.payload.decode("utf-8", "ignore"))
        self.flag_power_forecast = True
        if data:
            self.flag_get_data = True

    def regulation_load(self, power_fact):
        self.Load_delta_fact = self.power_forecast - power_fact
        self.Load_delta_fact_percent = self.Load_delta_fact / power_fact * 100
        if self.flag_power_forecast:
            K_freq = abs(self.Load_delta_fact_percent * self.K_freq_base)
            self.Delta_P = self.Load_delta_fact_percent * -K_freq
            self.flag_power_forecast = False
            print('Факт', power_fact)
            print('Прогноз', self.power_forecast)
            print('Отклонение по прогнозу ', self.Delta_P)
        pass
