from fastapi import FastAPI, Request, HTTPException, Header, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agent import Agent
import hashlib
import time
import pandas as pd
import agent as ag

app = FastAPI()

# Middleware CORS para permitir solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Cambiar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clase para mensajes individuales
class ChatMessage(BaseModel):
    role: str
    content: str

# Formato de solicitud de tipo chat/completion (compatible con OpenAI)
class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    stream: Optional[bool] = False  # Compatible con OpenAI

# Formato de solicitud para prompts simples
class PromptRequest(BaseModel):
    prompt: str

# Formato de respuesta para el endpoint /ask
class PromptResponse(BaseModel):
    answer: str
    results: list  # Lista de diccionarios (derivados de un DataFrame)

# Dataset de evaluación (en progreso)
class EvalSet(BaseModel):
    dataset: str

# Endpoint para probar prompts simples
@app.post("/ask", response_model=PromptResponse)
async def handle_prompt(request: PromptRequest):
    # Llama a la función del agente para generar una respuesta
    answer, df = ag.Agent().generate_response(request.prompt)

    return JSONResponse(content={
        "answer": answer,
        "results": df
    })

# Modelos disponibles simulando compatibilidad con OpenAI
available_models = [
    {
        "id": "gpt-3.5-turbo",
        "object": "model",
        "created": 1686935000,
        "owned_by": "openai"
    },
    {
        "id": "gpt-4",
        "object": "model",
        "created": 1686936000,
        "owned_by": "openai"
    }
]

# Endpoint para listar modelos (imitación OpenAI)
@app.get("/v1/models")
async def list_models():
    return JSONResponse(content={
        "object": "list",
        "data": available_models
    })

# Endpoint principal tipo chat/completion (respuesta mock)
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest, authorization: str = Header(default=None)):
    return {
        "id": "chatcmpl-" + hashlib.sha256(str(request.messages).encode()).hexdigest()[:24],
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": ChatMessage(role="assistant", content="Soy un asistente."),
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 19,
            "completion_tokens": 2,
            "total_tokens": 21,
            "prompt_tokens_details": {
                "cached_tokens": 0,
                "audio_tokens": 0
            },
            "completion_tokens_details": {
                "reasoning_tokens": 0,
                "audio_tokens": 0,
                "accepted_prediction_tokens": 0,
                "rejected_prediction_tokens": 0
            }
        },
        "service_tier": "default"
    }

# Soporte para método OPTIONS (preflight request desde el frontend)
@app.options("/v1/models")
async def options_models():
    return Response(
        status_code=204,
        headers={
            "Allow": "GET, POST, OPTIONS",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type"
        }
    )

# Endpoint para evaluación (pendiente de implementación)
@app.post("/eval")
async def make_evaluation(eval_set: EvalSet):
    results = 0  # Resultado simulado
    return JSONResponse(content={"results": results})

