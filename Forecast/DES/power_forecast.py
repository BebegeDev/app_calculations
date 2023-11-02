import json

import Interface.interface

interface = Interface.interface


class PowerForecast(interface.InterfaceForecast):

    def __init__(self, mqttc):
        self.flag_get_data = None
        self.flag_power_forecast = None
        self.power_forecast = 0
        self.mqttc = mqttc

    async def callback_data(self, topic="mpei/Forecast/Power_fact"):
        self.mqttc.message_callback_add(topic, self.get_data)

    def get_data(self, client, userdata, data):
        self.power_forecast = json.loads(data.payload.decode("utf-8", "ignore"))
        self.flag_power_forecast = True
        if data:
            self.flag_get_data = True
