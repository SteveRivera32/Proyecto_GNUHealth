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
        "id": "gnutest",
        "object": "model",
        "created": 1,
        "owned_by": "google-open-source"
    },
       {
        "id": "gemma3:4b",
        "object": "model",
        "created": 2,
        "owned_by": "premai-open-source"
    },
]

# Endpoint para listar modelos disponibles (para compatibilidad con clientes tipo OpenAI)
@app.get("/api/models")
async def list_models():
    print("/api/models fue consultado")
    return JSONResponse(content={
        "object": "list",
        "data": available_models
    })

# Endpoint de completación de chat estilo OpenAI (con respuesta generada por el modelo)
@app.post("/api/chat/completions")
async def chat_completions(request: ChatCompletionRequest, authorization: str = Header(default=None)):
    print("Recibido en /chat/completions")
    print("Modelo:", request.model)
    #print("Mensajes:", [m.content for m in request.messages])

    # Verificar si el modelo es válido
    if request.model not in [m["id"] for m in available_models]:
        raise HTTPException(status_code=404, detail="404: Model not listed in /api/models")

    # Para debug, ver si Ollama tiene ese modelo
    if request.model == "gnutest":
        print("⚠️ WARNING: gnutest no es un modelo real en Ollama (esto es solo un ID de prueba).")

    # ✅ Nueva validación correcta (la que te recomiendo poner)
    if not request.model:
        print("Modelo faltante")
        raise HTTPException(status_code=400, detail="Falta el modelo.")

    if request.messages is None:
        print("Messages es None (no permitido)")
        raise HTTPException(status_code=400, detail="Messages no puede ser None.")

    if len(request.messages) == 0:
        print("Messages vacío → respuesta vacía")
        return {
            "id": "premSQLChat-empty",
            "object": "chat.completion",
            "created": time.time(),
            "model": request.model,
            "choices": [{
                "message": ChatMessage(role="assistant", content=""),
            }]
        }

    # 🔥 Extraer system prompt (si existe)
    system_prompt = None
    for msg in request.messages:
        if msg.role == "system":
            system_prompt = msg.content
            break

    print("System prompt cargado\n" if system_prompt else "No system prompt\n")

    agent = ag.Agent(request.model)

    # Reconstruir chat_history desde request.messages (así se mantiene la conversación)
    agent.chat_history = [ { "role": m.role, "content": m.content } for m in request.messages ]

    chat_id = "premSQLChat-" + hashlib.sha256(str(request.messages).encode()).hexdigest()[:24]

    # Tomar el último mensaje del usuario
    user_question = None
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_question = msg.content
            break

    if not user_question:
        raise HTTPException(status_code=400, detail="No se encontró un mensaje de usuario válido.")

    response, tipo = agent.generate_response(user_question, system_prompt=system_prompt)

    if tipo in ["natural", "sql_result"]:
        if response.get("content", None):
            answer = response["content"]
        elif response.get("response", None):
            answer = response["response"]
        else:
            answer = "No se pudo generar una respuesta válida."
    elif tipo == "error":
        answer = response.get("error", f"Ocurrió un error inesperado. {response}")
    elif tipo == "error_handled":
        if "content" in response:
            answer = response["content"]
        elif "sql" in response:
            answer = f"Se corrigió la consulta: {response['sql']}"
        else:
            answer = "Se intentó corregir el error pero no se obtuvo una respuesta válida."
    else:
        answer = "No se pudo procesar la respuesta."

    return {
        "id": chat_id,
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