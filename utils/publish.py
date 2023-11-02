import csv


class Publish:

    def __init__(self, mqttc):
        self.flag_excluded = None
        self.power = None
        self.mqttc = mqttc

    def optimize_publish(self, optimize):
        if optimize.flag_excluded:
            list_engine = []
            self.power = 0
            for engine, idx in enumerate(optimize.cons_idx):
                if idx is not None:
                    list_engine.append(engine)
                    self.power += optimize.output_W.loc[idx, engine]
                    self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Consuming", optimize.input_L_J[idx, engine])
                    self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Power_DGU/current_generator_power",
                                       optimize.output_W.loc[idx, engine])
                    self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Job_status", 1)
            for engine in range(6):
                if engine not in list_engine:
                    self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Power_DGU/current_generator_power", 0)
                    self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Consuming", 0)
                    self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Job_status", 0)
        optimize.flag_excluded = False

    def regulation_frequency(self, frequency):
        if frequency.flag_frequency:
            self.mqttc.publish(f"mpei/Frequency/Changing_network_frequency_deviation", frequency.Freq_delta_fact)
            self.mqttc.publish(f"mpei/DES/Power/Power_gain", frequency.Delta_P)
            self.mqttc.publish(f"mpei/DES/Power/Your_power", frequency.P_DES_new)
            self.mqttc.publish(f"mpei/DES/Power/Current_power", frequency.load)
            frequency.flag_frequency = False
            # with open('result.csv', mode='a', encoding='utf-8', newline='') as file:
            #     writer = csv.writer(file)
            #     data_to_add = [
            #         frequency.P_DES_new,
            #         frequency.Delta_P,
            #         frequency.frequency,
            #         frequency.Freq_delta_fact,
            #         frequency.load
            #     ]
            #     writer.writerow(data_to_add)

    def regulation_load(self, forecast_load):
        if forecast_load.flag_power_forecast:
            forecast_load.flag_power_forecast = False
            self.mqttc.publish(f"mpei/DES/TEST_TOPIC", forecast_load.Delta_P)
