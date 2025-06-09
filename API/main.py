from fastapi import FastAPI, Request, HTTPException, Header, Response
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from agents.response_stream import stream_response
from models.chat import ChatCompletionRequest, ChatMessage, PromptRequest, PromptResponse, EvalSet
import agents.agent as ag
import hashlib
import time
import os
import json
from dotenv import load_dotenv

from typing import Optional
from fastapi import Header

# Cargar variables de entorno
load_dotenv()

# Inicializar FastAPI
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista de modelos disponibles
available_models = [
    {
        "id": "gemma3:4b",
        "object": "model",
        "created": 2,
        "owned_by": "premai-open-source"
    },
    {
        "id": "gemma3:12b-it-qat",
        "object": "model",
        "created": 3,
        "owned_by": "premai-open-source"
    },
    {
        "id": "gemma3:27b-it-qat",
        "object": "model",
        "created": 4,
        "owned_by": "premai-open-source"
    },
]

# Mapeo de modelos al formato que espera OpenWebUI/Ollama API
def get_tags_response_v2():
    return [
        {
            "name": m["id"],
            "modified_at": "2024-01-01T00:00:00Z",
            "size": 1000000000,
            "digest": "sha256:fakehash",
            "details": {
                "family": "custom",
                "parameter_size": "N/A",
                "quantization_level": "N/A"
            }
        } for m in available_models
    ]

def get_tags_response():
    return [
        {
            "name": m["id"],
            "model": m["id"],
            "modified_at": "2025-02-19T13:31:57.5607265-06:00",
            "size": 2019393189,
            "digest": "a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72",
            "details": {
                "parent_model": "",
                "format": "gguf",
                "family": m["id"].split(":")[0] if ":" in m["id"] else "custom",
                "families": [
                    m["id"].split(":")[0] if ":" in m["id"] else "custom"
                ],
                "parameter_size": "3.2B",
                "quantization_level": "Q4_K_M"
            }
        } for m in available_models
    ]

# /api/tags → usado por OpenWebUI para leer modelos
@app.get("/api/tags")
async def list_tags():
    print("/api/tags fue consultado")
    return JSONResponse(content={
        "models": get_tags_response()
    })

# /api/models → usado por OpenWebUI para leer modelos (estilo OpenAI)
@app.get("/api/models")
async def list_models(authorization: Optional[str] = Header(default=None)):
    print("/api/models fue consultado")
    print("Authorization header:", authorization)
    
    try:
        return JSONResponse(
            status_code=200,
            content={
                "object": "list",
                "data": [
                    {
                        "id": m["id"],
                        "object": "model",
                        "created": m["created"],
                        "owned_by": m["owned_by"]
                    } for m in available_models
                ]
            }
        )
    except Exception as e:
        print(f"Error en /api/models: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(e)
            }
        )

# /api/version → versión ficticia
@app.get("/api/version")
async def api_version():
    print("/api/version fue consultado")
    return JSONResponse(content={
        "version": "1.0.0",
    })

# /api/generate → endpoint estilo Ollama
@app.post("/api/generate")
async def generate_ollama_style(request: Request):
    body = await request.json()
    print("Recibido en /api/generate:", body)

    model_id = body.get("model", "gnutest")
    prompt = body.get("prompt", "")

    if model_id not in [m["id"] for m in available_models]:
        raise HTTPException(status_code=404, detail="404: Model not listed in /api/tags")

    agent = ag.Agent(model_id)
    response, tipo = agent.generate_response(prompt)

    if tipo in ["natural", "sql_result"]:
        answer = response.get("content") or response.get("response") or ""
    elif tipo == "error":
        answer = response.get("error", "Error inesperado.")
    else:
        answer = "No se pudo procesar la respuesta."

    return JSONResponse(content={
        "model": model_id,
        "created_at": "2024-01-01T00:00:00Z",
        "message": {
            "role": "assistant",
            "content": answer
        },
        "done": True
    })

# /api/chat/completions → endpoint estilo OpenAI
@app.post("/api/chat")
async def chat_completions(request: ChatCompletionRequest, authorization: str = Header(default=None)):
    print("Recibido en /api/chat")
    print("Modelo:", request.model)

    if request.model not in [m["id"] for m in available_models]:
        print("Modelo no encontrado en la lista de modelos disponibles.")
        raise HTTPException(status_code=404, detail="404: Model not listed in /api/models")

    if not request.model:
        print("Falta el modelo en la solicitud.")
        raise HTTPException(status_code=400, detail="Falta el modelo.")

    if request.messages is None:
        print("Messages es None en la solicitud.")
        raise HTTPException(status_code=400, detail="Messages no puede ser None.")

    if len(request.messages) == 0:
        return {
            "id": "premSQLChat-empty",
            "object": "chat.completion",
            "created": time.time(),
            "model": request.model,
            "choices": [{
                "message": ChatMessage(role="assistant", content=""),
            }]
        }

    print("Procesando mensajes de la solicitud...")
    system_prompt = None
    for msg in request.messages:
        if msg.role == "system":
            system_prompt = msg.content
            break

    agent = ag.Agent(request.model)
    agent.chat_history = [{ "role": m.role, "content": m.content } for m in request.messages]

    chat_id = "premSQLChat-" + hashlib.sha256(str(request.messages).encode()).hexdigest()[:24]

    user_question = None
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_question = msg.content
            break

    if not user_question:
        raise HTTPException(status_code=400, detail="No se encontró un mensaje de usuario válido.")

    response, tipo = agent.generate_response(user_question, system_prompt=system_prompt)

    if tipo in ["natural", "sql_result"]:
        answer = response.get("content") or response.get("response") or ""
    elif tipo == "error":
        answer = response.get("error", "Error inesperado.")
    elif tipo == "error_handled":
        if "content" in response:
            answer = response["content"]
        elif "sql" in response:
            answer = f"Se corrigió la consulta: {response['sql']}"
        else:
            answer = "Se intentó corregir el error pero no se obtuvo una respuesta válida."
    else:
        answer = "No se pudo procesar la respuesta."

    # Armar la respuesta en el formato esperado
    respuesta = {
        "model": request.model,
        "created_at": time.time(),
        "message": {
            "role": "assistant",
            "content": answer
        },
        "done_reason": "stop",
        "done": True,
        "total_duration": 5551148643,
        "load_duration": 4891918024,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 464582854,
        "eval_count": 13,
        "eval_duration": 192853402
    }

    return respuesta 

# Endpoint para evaluación (dummy)
@app.post("/eval")
async def make_evaluation(eval_set: EvalSet):
    results = 0
    return JSONResponse(content={"results": results})