from fastapi import FastAPI, Request, HTTPException, Header, Response
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from agents.response_stream import stream_response
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
# Updated CORS settings to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Alternatively, you can specify specific origins if you know them:
# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://127.0.0.1",
#     "http://127.0.0.1:8080",
#     "https://your-production-domain.com",
# ]
# 
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

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
        "id": "tinyllama",
        "object": "model",
        "created": 1,
        "owned_by": "google-open-source"
    },
     {
        "id": "anindya/prem1b-sql-ollama-fp116",
        "object": "model",
        "created": 2,
        "owned_by": "premai-open-source"
    },
       {
        "id": "gemma2",
        "object": "model",
        "created": 2,
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

    agent = ag.Agent(request.model)
    
    stream=request.stream,
    chat_id="premSQLChat-" + hashlib.sha256(str(request.messages).encode()).hexdigest()[:24]
    #Text streaming no soportado por el momento
    print("streaming",stream)

    #Vamos a realziar dejando este codgo como siempre boolean.
    #Al parecer se necesta nvestigar sobre algunos metodos asincronos para este tipo de generacion.
 
    #Atencion la funcion de streaming esta rota desabilitar text-streamin en open web ui
    if  stream==True:
        answer = agent.generate_natural_response_stream(request.messages[-1].content)
        return StreamingResponse(stream_response(answer,request.model,chat_id,time.time()), media_type="text/event-stream")

    else:
        # Devolver la respuesta formateada como si fuera OpenAI API
        answer = agent.generate_sql_response(request.messages[-1].content)
   
        return {
            "id":chat_id ,
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