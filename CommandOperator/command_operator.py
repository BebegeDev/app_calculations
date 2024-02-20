from Interface.interface import InterfaceCallback

interface = InterfaceCallback


class Command(InterfaceCallback):

    def __init__(self, mqttc):
        self.parsed_data = None
        self.mqttc = mqttc

    def callback_data(self, topic='mpei/command/on_off'):
        self.mqttc.message_callback_add(topic, self.get_data)

    def get_data(self, client, userdata, data):
        try:
            self.parsed_data = int(data.payload.decode())
            if self.parsed_data:
                print("Команда вкл.", self.parsed_data)
            else:
                print('Команды выкл', self.parsed_data)
        except Exception as e:
            print(f"Ошибка при обработке данных: {e}")

    def validate_data(self, data):
        pass
