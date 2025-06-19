
from google import genai
from typing import List
from ollama import Client
import os
"""
This new module will run on a google DEV API model.
"""
class TextGeneratorGooogle:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = genai.Client(os.getenv("OPENAI_API_KEY", ""))
        

    def generate(self, messages: List[dict]) -> str:
        """
        Envía un array de mensajes (tipo OpenAI chat) al modelo y obtiene una respuesta.
        
        Args:
            messages (List[dict]): Lista de mensajes con roles y contenidos.

        Returns:
            str: Respuesta generada por el modelo.
        """
        print("Enviando mensajes a Ollama:", messages)

        model = genai.GenerativeModel('gemini-pro')

        chat = model.start_chat(history=[]) # You can provide initial chat history if needed
        response = chat.send_message(messages)
        print(f"AI: {response.text}")
        print("Respuesta de Ollama:", response)
        return response.text

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
