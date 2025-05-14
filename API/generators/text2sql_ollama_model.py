from typing import Optional
from premsql.generators.base import Text2SQLGeneratorBase
from premsql.logger import setup_console_logger
import os
logger = setup_console_logger(name="[OLLAMA-GENERATOR]")

try:
    from ollama import Client
except ImportError:
    logger.warn("Ensure ollama is installed")
    logger.warn("Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
    logger.warn("Install Ollama python: pip install ollama")


class Text2SQLGeneratorOllama(Text2SQLGeneratorBase):
    """
    Generador de texto a SQL usando un modelo alojado en Ollama.

    Esta clase se conecta a un modelo LLM a través del cliente Ollama para generar consultas SQL
    a partir de prompts en lenguaje natural.

    Atributos:
        model_name (str): Nombre del modelo LLM en Ollama.
        _kwargs (dict): Argumentos adicionales que pueden ser utilizados por subclases.
    """

    def __init__(
        self, 
        model_name: str,
        experiment_name: str,
        type: str,
        experiment_folder: Optional[str] = None,
        **kwargs
    ):
        """
        Inicializa el generador de SQL con la configuración del experimento.

        Args:
            model_name (str): Nombre del modelo en Ollama.
            experiment_name (str): Nombre del experimento o sesión.
            type (str): Tipo de modelo o prueba.
            experiment_folder (Optional[str]): Carpeta para guardar resultados (opcional).
            **kwargs: Parámetros adicionales para la clase base.
        """
        self._kwargs = kwargs
        self.model_name = model_name

        # Inicializa la clase base
        super().__init__(
            experiment_name=experiment_name,
            experiment_folder=experiment_folder,
            type=type
        )
    
    @property
    def load_client(self):
        # Retorna el cliente Ollama para conectarse al modelo
        print(os.getenv("OLLAMA_URL", "http://localhost:11434"))
        return Client(host=os.getenv("OLLAMA_URL", "http://localhost:11434"))
    
    @property
    def load_tokenizer(self):
        # No se utiliza tokenizador explícito en este generador
        pass

    @property
    def model_name_or_path(self):
        # Devuelve el nombre del modelo especificado
        return self.model_name

    def generate(
        self,
        data_blob: dict,
        temperature: Optional[float] = 0.0,
        max_new_tokens: Optional[int] = 256,
        postprocess: Optional[bool] = True,
        **kwargs
    ) -> str:
        """
        Genera una respuesta SQL a partir de un prompt en lenguaje natural.

        Args:
            data_blob (dict): Diccionario que debe incluir una clave "prompt" con el texto de entrada.
            temperature (float, opcional): Controla la aleatoriedad del modelo. Default es 0.0.
            max_new_tokens (int, opcional): Máximo número de tokens nuevos. Default es 256.
            postprocess (bool, opcional): Si se aplica post-procesamiento al resultado. Default es True.
            **kwargs: Parámetros adicionales que pueden ser utilizados.

        Returns:
            str: Consulta SQL generada por el modelo.
        """
        prompt = data_blob["prompt"]

        # Enviar prompt al modelo y obtener respuesta
        response = self.load_client.chat(
            model=self.model_name_or_path,
            messages=[{"role": "user", "content": prompt}],
            options=dict(
                temperature=temperature,
                num_ctx=2048 + max_new_tokens
            )
        )["message"]["content"]

        # Retorna la respuesta postprocesada si es necesario
        print(response)
        return self.postprocess(output_string=response) if postprocess else response
