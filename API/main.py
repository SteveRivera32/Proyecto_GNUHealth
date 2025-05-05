from fastapi import FastAPI, Request, HTTPException, Header, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import agent as ag
import hashlib
import time
import pandas as pd


app = FastAPI()

# Middleware CORS para permitir solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Cambiar en producción
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
        "id": "gemma3:4b",
        "object": "model",
        "created": 1686935000,
        "owned_by": "premai-open-source"
    },

]

# Endpoint para listar modelos (imitación OpenAI)
@app.get("/api/models")
async def list_models():
    return JSONResponse(content={
        "object": "list",
        "data": available_models
    })

# Endpoint principal tipo chat/completion (respuesta mock)
@app.post("/api/chat/completions")
async def chat_completions(request: ChatCompletionRequest, authorization: str = Header(default=None)):
    
    return {
        "id":"premSQLChat-" + hashlib.sha256(str(request.messages).encode()).hexdigest()[:24] ,
        "object": "chat.completion",
        "created": time.time(),
        "model": request.model,
        "choices": [{
            "message": ChatMessage(role="assistant", content= "Here's the data in JSON format:\n\n```json\n[\n  {\"Nombre\": \"Diego\", \"Edad\": 23, \"Ciudad\": \"Tegucigalpa\"},\n  {\"Nombre\": \"Mariana\", \"Edad\": 21, \"Ciudad\": \"San Pedro\"},\n  {\"Nombre\": \"Alejandro\", \"Edad\": 25, \"Ciudad\": \"La Ceiba\"}\n]\n```"),
            
        }]
    }

# Soporte para método OPTIONS (preflight request desde el frontend)
@app.options("/api/models")
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

