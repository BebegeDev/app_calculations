from abc import ABC, abstractmethod


class InterfaceForecast(ABC):

    @abstractmethod
    def callback_data(self, topic):
        pass

    @abstractmethod
    def get_data(self, client, userdata, data):
        pass
