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
import httpx

from typing import Optional, List, Dict
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

# Configuración de Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODELS_ENDPOINT = f"{OLLAMA_BASE_URL}/api/tags"

# Cache para modelos
available_models_cache = []
last_cache_update = 0
CACHE_TTL = 300  # 5 minutos en segundos

async def fetch_ollama_models() -> List[Dict]:
    """Obtiene la lista de modelos disponibles desde Ollama"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OLLAMA_MODELS_ENDPOINT, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
    except Exception as e:
        print(f"Error al obtener modelos de Ollama: {str(e)}")
        return []

async def get_available_models() -> List[Dict]:
    """Obtiene los modelos disponibles, usando cache si es válido"""
    global available_models_cache, last_cache_update
    
    current_time = time.time()
    if current_time - last_cache_update < CACHE_TTL and available_models_cache:
        return available_models_cache
    
    ollama_models = await fetch_ollama_models()
    
    # Transformar los modelos al formato que espera tu API
    transformed_models = []
    for idx, model in enumerate(ollama_models, start=1):
        model_name = model.get("name", "")
        transformed_models.append({
            "id": model_name,
            "object": "model",
            "created": idx,
            "owned_by": "ollama"
        })
    
    available_models_cache = transformed_models
    last_cache_update = current_time
    return transformed_models

async def get_tags_response(models: List[Dict]) -> List[Dict]:
    """Genera la respuesta para el endpoint /api/tags con datos reales de Ollama"""
    response = []
    
    async with httpx.AsyncClient() as client:
        for m in models:
            try:
                # Obtener detalles específicos del modelo desde Ollama
                model_info = await client.post(f"{OLLAMA_BASE_URL}/api/show", json={"name": m["id"]})
                model_info.raise_for_status()
                model_data = model_info.json()
                
                response.append({
                    "name": m["id"],
                    "model": m["id"],
                    "modified_at": model_data.get("modified_at", "2025-02-19T13:31:57.5607265-06:00"),
                    "size": model_data.get("size", 2019393189),
                    "digest": model_data.get("digest", "a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72"),
                    "details": {
                        "parent_model": model_data.get("parent_model", ""),
                        "format": model_data.get("format", "gguf"),
                        "family": m["id"].split(":")[0] if ":" in m["id"] else "custom",
                        "families": [
                            m["id"].split(":")[0] if ":" in m["id"] else "custom"
                        ],
                        "parameter_size": model_data.get("parameter_size", "3.2B"),
                        "quantization_level": model_data.get("quantization_level", "Q4_K_M")
                    }
                })
            except Exception as e:
                print(f"Error obteniendo detalles para el modelo {m['id']}: {str(e)}")
                # Fallback a valores por defecto si hay error
                response.append({
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
                })
    
    return response

# /api/tags → usado por OpenWebUI para leer modelos
@app.get("/api/tags")
async def list_tags():
    print("/api/tags fue consultado")
    models = await get_available_models()
    models_details = await get_tags_response(models)
    return JSONResponse(content={
        "models": models_details
    })

# /api/models → usado por OpenWebUI para leer modelos (estilo OpenAI)
@app.get("/api/models")
async def list_models(authorization: Optional[str] = Header(default=None)):
    print("/api/models fue consultado")
    print("Authorization header:", authorization)
    
    try:
        models = await get_available_models()
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
                    } for m in models
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

    models = await get_available_models()
    if model_id not in [m["id"] for m in models]:
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

    models = await get_available_models()
    if request.model not in [m["id"] for m in models]:
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

    start_time = time.time()
    print("Procesando mensajes de la solicitud...")
    
    # Procesamiento del sistema prompt y mensajes
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

    # Medición del tiempo real de procesamiento
    processing_start = time.time()
    response, tipo = agent.generate_response(user_question, system_prompt=system_prompt)
    processing_duration = time.time() - processing_start

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

    # Tiempos realistas basados en el procesamiento real
    total_duration = time.time() - start_time
    load_duration = total_duration * 0.8  # 80% del tiempo es "carga"
    eval_duration = total_duration * 0.15  # 15% es evaluación
    prompt_eval_duration = total_duration * 0.05  # 5% es evaluación del prompt

    # Estimar conteos basados en la longitud de la respuesta
    eval_count = max(10, len(answer.split()) // 5)
    prompt_eval_count = max(5, len(user_question.split()) // 3)

    # Armar la respuesta con métricas realistas
    respuesta = {
        "model": request.model,
        "created_at": start_time,
        "message": {
            "role": "assistant",
            "content": answer
        },
        "done_reason": "stop",
        "done": True,
        "total_duration": int(total_duration * 1e9),  # Convertir a nanosegundos
        "load_duration": int(load_duration * 1e9),
        "prompt_eval_count": prompt_eval_count,
        "prompt_eval_duration": int(prompt_eval_duration * 1e9),
        "eval_count": eval_count,
        "eval_duration": int(eval_duration * 1e9)
    }

    return respuesta

# Endpoint para evaluación (dummy)
@app.post("/eval")
async def make_evaluation(eval_set: EvalSet):
    results = 0
    return JSONResponse(content={"results": results})