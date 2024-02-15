from abc import ABC, abstractmethod


class InterfaceCallback(ABC):

    @abstractmethod
    async def callback_data(self, topic):
        pass

    @abstractmethod
    def get_data(self, client, userdata, data):
        pass

    @abstractmethod
    def validate_data(self, data):
        pass
