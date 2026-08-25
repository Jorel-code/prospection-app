from abc import ABC, abstractmethod

class IAIMessageGenerator(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, channel: str) -> "GeneratedMessage":
        ...