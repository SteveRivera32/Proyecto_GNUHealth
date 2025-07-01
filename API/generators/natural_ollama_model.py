from typing import List
from ollama import Client
import os

class TextGenerator:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))

    def generate(self, messages: List[dict]) -> str:
        """
        Envía un array de mensajes (tipo OpenAI chat) al modelo y obtiene una respuesta.
        
        Args:
            messages (List[dict]): Lista de mensajes con roles y contenidos.

        Returns:
            str: Respuesta generada por el modelo.
        """
        log=""
        for ms in messages:
            log+="\n"+str(ms)
        with open("./log.txt","a") as file:
            file.write(log)

        print("Enviando mensajes a Ollama:"+"*"*10)
        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            stream=False,
        )
        print("Respuesta de Ollama:", response)

        with open("./log.txt","a") as file:
            file.write("\n"+str(response["message"]))
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
