# models/base_model.py
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs):
        pass

    @abstractmethod
    def chat(self, messages: list, **kwargs):
        pass

    @abstractmethod
    def embeddings(self, text: str):
        pass
