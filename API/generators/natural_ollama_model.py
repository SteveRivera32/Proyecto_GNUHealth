from ollama import Client

# Conecta al servidor local de Ollama
client = Client(host='http://localhost:11434')


class TextGenerator:
    """
    Clase que encapsula la generación de texto natural utilizando el modelo Ollama.

    Atributos:
        model_name (str): Nombre del modelo cargado en Ollama.
        client (ollama.Client): Cliente para comunicarse con el servidor Ollama.
    """
    
    def __init__(self, model_name: str):
        """
        Inicializa el generador de texto con el modelo especificado y el cliente Ollama.

        Args:
            model_name (str): Nombre del modelo cargado en el servidor Ollama.
        """
        self.model_name = model_name
        self.client = Client(host='http://localhost:11434')  # Conexión al servidor Ollama

    def generate(self, prompt: str) -> str:
        """
        Envía un prompt al modelo y obtiene una respuesta generada en lenguaje natural.

        Args:
            prompt (str): Texto de entrada que será procesado por el modelo.

        Returns:
            str: Respuesta generada por el modelo Ollama.
        """
        response = self.client.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
