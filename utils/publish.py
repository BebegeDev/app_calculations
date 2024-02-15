class Publish:

    def __init__(self, mqttc):
        self.flag_excluded = None
        self.power = None
        self.mqttc = mqttc

    def optimize_publish(self, optimize):
        list_engine = []
        self.power = 0
        for engine, idx in enumerate(optimize.cons_idx):
            if idx is not None:
                list_engine.append(engine)
                self.power += optimize.output_W.loc[idx, engine]
                self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Consuming", optimize.output_L[idx, engine])
                self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Power_DGU/current_generator_power",
                                   optimize.output_W.loc[idx, engine])
                self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Job_status", 1)
        for engine in range(6):
            if engine not in list_engine:
                self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Power_DGU/current_generator_power", 0)
                self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Consuming", 0)
                self.mqttc.publish(f"mpei/DES/DGU/{engine + 1}/Job_status", 0)

    def regulation_frequency(self, frequency, data_path):
        self.mqttc.publish(f"mpei/Frequency/Changing_network_frequency_deviation", frequency.Freq_delta_fact)
        self.mqttc.publish(f"mpei/DES/Power/Power_gain", frequency.Delta_P)
        self.mqttc.publish(f"mpei/DES/Power/Your_power", frequency.P_DES_new)
        self.mqttc.publish(f"mpei/DES/Power/Current_power", frequency.load)
        data_to_add = [
            frequency.P_DES_new,
            frequency.Delta_P,
            frequency.frequency,
            frequency.Freq_delta_fact,
            frequency.load
        ]
        # data_path.open_csv('result.csv', mode='a', name_column=data_to_add)

    def regulation_load(self, forecast_load):
        self.mqttc.publish(f"mpei/DES/TEST_TOPIC", forecast_load.Delta_P)
