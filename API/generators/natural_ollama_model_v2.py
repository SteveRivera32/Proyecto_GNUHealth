from typing import List
from ollama import Client
import os

class TextGenerator:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = Client(host=os.getenv("OLLAMA_URL", "http://localhost:11434"))

    def generate(self, messages: List[dict]) -> str:
        """
        Envía un array de mensajes (tipo OpenAI chat) al modelo y obtiene una respuesta.
        
        Args:
            messages (List[dict]): Lista de mensajes con roles y contenidos.

        Returns:
            str: Respuesta generada por el modelo.
        """
        print("Enviando mensajes a Ollama:", messages)
        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            stream=False,
        )
        print("Respuesta de Ollama:", response)
        return response["message"]["content"]

    def generate_stream(self, messages: List[dict]):
        """
        Envía un array de mensajes (tipo OpenAI chat) al modelo y obtiene una respuesta en streaming.
        
        Args:
            messages (List[dict]): Lista de mensajes con roles y contenidos.

        Returns:
            Generator: Respuesta en streaming.
        """
        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            stream=True,
        )
        return response
