import json

import Interface.interface

interface = Interface.interface


class PowerForecast(interface.InterfaceForecast):

    def __init__(self, mqttc):
        self.flag_power_forecast = None
        self.power_forecast = 0
        self.mqttc = mqttc

    def callback_data(self, topic="mpei/Forecast/Load"):
        self.mqttc.message_callback_add(topic, self.get_data)

    def get_data(self, client, userdata, data):
        self.power_forecast = json.loads(data.payload.decode("utf-8", "ignore"))
        self.flag_power_forecast = True
