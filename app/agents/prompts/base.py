from abc import ABC
from abc import abstractmethod


class BasePromptProvider(ABC):
    """
    Base interface for all prompt providers.

    Every prompt provider is responsible for supplying a
    specific piece of the overall prompt.
    """

    @abstractmethod
    def get_prompt(self) -> str:
        """
        Return the prompt text.
        """
        raise NotImplementedError