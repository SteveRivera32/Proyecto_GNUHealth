# Text Streamng in Open AI API:


Perfecto, gracias por la corrección. Si estás usando `stream=True` en `ollama.chat(...)`, el cliente de Python de Ollama devuelve **chunks JSON como este**:

```json
{
  "model": "llama3.2",
  "created_at": "2023-08-04T08:52:19.385406455-07:00",
  "response": "The",
  "done": false
}
```

Al final, se emite un último chunk con:

```json
{
  "model": "llama3.2",
  "created_at": "...",
  "response": "",
  "done": true
}
```

---

### ✅ Entonces, ¿cómo lo adaptamos a FastAPI para emitir chunks estilo **ChatGPT** (`choices`, `delta`, etc.)?

Aquí tienes una versión ajustada del endpoint FastAPI que toma los chunks de Ollama, los transforma al formato estilo OpenAI (`chat.completion.chunk`), y los envía como Server-Sent Events:

---

### 🧩 FastAPI + Ollama stream → formato tipo OpenAI

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import ollama
import time
import json
import uuid

app = FastAPI()
client = ollama.Client()

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    model = body.get("model", "llama3")

    chat_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created_time = int(time.time())

    def event_stream():
        response = client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in response:
            if chunk.get("done"):
                # Final chunk
                final_chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": chunk.get("model"),
                    "system_fingerprint": "fp_dummy",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {},
                            "logprobs": None,
                            "finish_reason": "stop"
                        }
                    ]
                }
                yield f"data: {json.dumps(final_chunk)}\n\n"
                yield "data: [DONE]\n\n"
                break
            else:
                # Transform Ollama's "response" into OpenAI-style delta
                delta = {"role": "assistant", "content": chunk['message']['content']}
                json_chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": chunk.get("model"),
                    "system_fingerprint": "fp_dummy",
                    "choices": [
                        {
                            "index": 0,
                            "delta": delta,
                            "logprobs": None,
                            "finish_reason": None
                        }
                    ]
                }
                yield f"data: {json.dumps(json_chunk)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

---

### 🚀 Resultado:

Esto imita la API de streaming de OpenAI (`chat.completions` con `delta`) pero usando Ollama como backend.

### 🎯 Ventajas:

* Compatible con frontends hechos para ChatGPT/OpenAI.
* Usa SSE (`text/event-stream`), ideal para UIs en tiempo real.
* Muy fácil de adaptar para `messages` en lugar de un solo `prompt`.

---

¿Quieres que esto también acepte múltiples `messages` como entrada, en vez de solo `prompt` plano?
