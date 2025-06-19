¡Hola! Con gusto te ayudo a generar la documentación de tu API basándome en el código proporcionado y el contexto de la API de Ollama.

Primero, analizaré tu API y generaré una documentación estructurada en español.

# Documentación de la API de Emulación de Ollama

## Descripción General
Esta API emula el comportamiento de la API de Ollama, proporcionando endpoints compatibles para la integración con servicios como OpenWebUI. La API está construida con FastAPI y soporta operaciones similares a las de Ollama para el manejo de modelos de lenguaje.

## Endpoints Disponibles

### 1. Listar Modelos (Estilo Ollama)
```
GET /api/tags
```
Este endpoint devuelve la lista de modelos disponibles en el formato esperado por OpenWebUI.

#### Respuesta
```json
{
  "models": [
    {
      "name": "nombre_modelo",
      "model": "nombre_modelo",
      "modified_at": "2025-02-19T13:31:57.5607265-06:00",
      "size": 2019393189,
      "digest": "hash_del_modelo",
      "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "familia_modelo",
        "families": ["familia_modelo"],
        "parameter_size": "3.2B",
        "quantization_level": "Q4_K_M"
      }
    }
  ]
}
```

### 2. Listar Modelos (Estilo OpenAI)
```
GET /api/models
```
Endpoint compatible con el formato OpenAI para listar modelos disponibles.

#### Headers
- `Authorization` (opcional): Token de autorización

#### Respuesta
```json
{
  "object": "list",
  "data": [
    {
      "id": "nombre_modelo",
      "object": "model",
      "created": 1234567890,
      "owned_by": "ollama"
    }
  ]
}
```

### 3. Generar Respuesta (Estilo Ollama)
```
POST /api/generate
```
Endpoint para generar respuestas usando el modelo especificado.

#### Cuerpo de la Petición
```json
{
  "model": "nombre_modelo",
  "prompt": "texto_prompt"
}
```

#### Respuesta
```json
{
  "model": "nombre_modelo",
  "created_at": "2024-01-01T00:00:00Z",
  "message": {
    "role": "assistant",
    "content": "respuesta_generada"
  },
  "done": true
}
```

### 4. Chat Completions (Estilo OpenAI)
```
POST /api/chat
```
Endpoint para interacciones de chat, compatible con el formato OpenAI.

#### Headers
- `Authorization` (opcional): Token de autorización

#### Cuerpo de la Petición
```json
{
  "model": "nombre_modelo",
  "messages": [
    {
      "role": "system",
      "content": "instrucciones_sistema"
    },
    {
      "role": "user",
      "content": "mensaje_usuario"
    }
  ]
}
```

#### Respuesta
```json
{
  "model": "nombre_modelo",
  "created_at": 1234567890,
  "message": {
    "role": "assistant",
    "content": "respuesta_generada"
  },
  "done": true,
  "done_reason": "stop",
  "total_duration": 1000000000,
  "load_duration": 800000000,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 50000000,
  "eval_count": 50,
  "eval_duration": 150000000
}
```

### 5. Versión de la API
```
GET /api/version
```
Devuelve la versión actual de la API.

#### Respuesta
```json
{
  "version": "1.0.0"
}
```

## Configuración
La API utiliza las siguientes variables de entorno:
- `OLLAMA_BASE_URL`: URL base de Ollama (por defecto: "http://localhost:11434")

## Manejo de Errores
La API implementa los siguientes códigos de error:
- `404`: Modelo no encontrado
- `400`: Solicitud incorrecta
- `500`: Error interno del servidor

