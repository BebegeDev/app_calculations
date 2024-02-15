import json
from Interface.interface import InterfaceCallback

interface = InterfaceCallback


class Frequency(InterfaceCallback):
    """

    Класс предназначен для расчета отклонения частоты
    """
    def __init__(self, mqttc):
        self.flag_get_data = None
        self.load = 0
        self.Freq_delta_fact_percent = None
        self.Freq_delta_fact = None
        self.flag_frequency = False
        self.frequency = 0
        self.K_freq_base = -1.5
        self.P_DES_new = 0
        self.Delta_P = 0
        self.mqttc = mqttc

    async def callback_data(self, topic="mpei/Frequency/frequency"):
        """

        :param topic: топик для подписки
        """
        self.mqttc.message_callback_add(topic, self.get_data)

    def get_data(self, client, userdata, data):
        """

        :param client: клиент Connected
        :param userdata: дата от клиента
        :param data: полезная нагрузка
        """
        try:
            parsed_data = json.loads(data.payload.decode("utf-8", "ignore"))
            self.validate_data(data)
            if self.flag_get_data:
                self.frequency = parsed_data
                self.flag_frequency = True
            else:
                print("Получены некорректные данные freq.")
        except Exception as e:
            print(f"Ошибка при обработке данных: {e}")
            self.flag_get_data = False

    def regulation_frequency(self):
        """

        Метод расчета отклонения частоты от нормы.
        """
        self.Freq_delta_fact = self.frequency - 50
        self.Freq_delta_fact_percent = self.Freq_delta_fact / 50 * 100
        if self.flag_frequency:
            K_freq = abs(self.Freq_delta_fact_percent * self.K_freq_base)
            self.Delta_P = self.Freq_delta_fact_percent * -K_freq
            # self.flag_frequency = False
            print('Частота', self.frequency)
            print('Отклонение по частоте', self.Delta_P)

    def validate_data(self, data):
        """

        :param data: необходимый флаг (временный)
        """
        if data:
            self.flag_get_data = True
