from abc import ABCMeta, abstractmethod
from typing import Any


class Producer(metaclass=ABCMeta):
    """Base class for Producers

    A promise that all Producers will have send_message
    """

    @abstractmethod
    async def send_message(self, data: dict[str, Any], producer_specifics: dict[str, Any]) -> None:
        pass
