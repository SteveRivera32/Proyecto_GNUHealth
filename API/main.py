from fastapi import FastAPI, Request, HTTPException, Header, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models.chat import ChatCompletionRequest, ChatMessage, PromptRequest, PromptResponse, EvalSet
import agents.agent as ag
import hashlib
import time
import os
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Inicializar la aplicación FastAPI
app = FastAPI()

# Middleware para permitir solicitudes desde otras fuentes (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("OPENWEB_UI_URL")],  # Reemplazar con dominio real en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint para procesar prompts y devolver respuestas en formato PromptResponse
@app.post("/ask", response_model=PromptResponse)
async def handle_prompt(request: PromptRequest):
    # Instanciar el agente con el modelo definido en .env
    agent = ag.Agent(os.getenv("MODEL_NAME"))

    # Generar respuesta y dataframe con resultados
    answer, df = agent.generate_response(request.prompt)

    # Devolver la respuesta en formato JSON
    return JSONResponse(content={
        "answer": answer,
        "results": df
    })

# Lista de modelos disponibles (imitando API de OpenAI)
available_models = [
    {
        "id": os.getenv('MODEL_NAME'),
        "object": "model",
        "created": 1686935000,
        "owned_by": "premai-open-source"
    },
]

# Endpoint para listar modelos disponibles (para compatibilidad con clientes tipo OpenAI)
@app.get("/api/models")
async def list_models():
    return JSONResponse(content={
        "object": "list",
        "data": available_models
    })

# Endpoint de completación de chat estilo OpenAI (con respuesta generada por el modelo)
@app.post("/api/chat/completions")
async def chat_completions(request: ChatCompletionRequest, authorization: str = Header(default=None)):
    # Crear agente y generar respuesta natural del modelo (último mensaje del usuario)
    agent = ag.Agent(os.getenv("MODEL_NAME"))
    answer = agent.generate_natural_response(request.messages[-1].content)
    #answer = agent.generate_sql_response(request.messages[-1].content)  # Alternativa para generar SQL

    # Devolver la respuesta formateada como si fuera OpenAI API
    return {
        "id": "premSQLChat-" + hashlib.sha256(str(request.messages).encode()).hexdigest()[:24],
        "object": "chat.completion",
        "created": time.time(),
        "model": request.model,
        "choices": [{
            "message": ChatMessage(role="assistant", content=answer),
        }]
    }

# Soporte para solicitudes OPTIONS desde frontend (preflight)
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

# Endpoint de evaluación (pendiente de implementación)
@app.post("/eval")
async def make_evaluation(eval_set: EvalSet):
    # Resultado simulado de evaluación
    results = 0
    return JSONResponse(content={"results": results})
