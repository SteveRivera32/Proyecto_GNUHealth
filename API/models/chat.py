from pydantic import BaseModel
from typing import List, Optional

# Clase para mensajes individuales usados en chats estilo OpenAI
class ChatMessage(BaseModel):
    """
    Representa un mensaje en una conversación de chat.

    Atributos:
        role (str): Rol del emisor (por ejemplo, "user", "assistant").
        content (str): Contenido textual del mensaje.
    """
    role: str
    content: str

# Solicitud de tipo chat/completion (compatible con el formato OpenAI)
class ChatCompletionRequest(BaseModel):
    """
    Formato de solicitud para completar una conversación estilo chat.

    Atributos:
        model (str): Nombre del modelo LLM a utilizar.
        messages (List[ChatMessage]): Lista de mensajes previos (contexto).
        max_tokens (Optional[int]): Límite de tokens para la respuesta.
        temperature (Optional[float]): Grado de aleatoriedad en la respuesta.
        top_p (Optional[float]): Top-p sampling (por defecto 1.0).
        stream (Optional[bool]): Si se desea respuesta en streaming.
    """
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    stream: Optional[bool] = False  # Compatible con OpenAI

# Solicitud para prompts simples (sin contexto de chat)
class PromptRequest(BaseModel):
    """
    Formato de solicitud para enviar un prompt directo al modelo.

    Atributos:
        prompt (str): Texto o pregunta que se envía al modelo.
    """
    prompt: str

# Respuesta del endpoint /ask
class PromptResponse(BaseModel):
    """
    Formato de respuesta para un prompt directo.

    Atributos:
        answer (str): Respuesta generada por el modelo.
        results (list): Resultados estructurados (como lista de diccionarios o dataframe).
    """
    answer: str
    results: list  # Lista de diccionarios (derivados de un DataFrame)

# Conjunto de datos de evaluación para pruebas automáticas
class EvalSet(BaseModel):
    """
    Estructura para enviar datasets de evaluación.

    Atributos:
        dataset (str): Nombre o contenido del dataset a evaluar.
    """
    dataset: str

