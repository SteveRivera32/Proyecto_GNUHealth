# Como usar este modulo de forma aislada?

debes create un container de Redis-Stack  acorde a https://hub.docker.com/r/redis/redis-stack

Aquí tienes la documentación en formato Markdown para el módulo redis_kb_module.py, explicando su propósito, funciones y los parámetros de entrada de cada una:

---

# Documentación del Módulo `redis_kb_module.py`

Este módulo proporciona utilidades para conectar y gestionar una base de datos vectorial en Redis, utilizando documentos de texto que son convertidos en vectores mediante modelos de embeddings. Está diseñado para almacenar, indexar y recuperar información relevante de tablas de una base de datos, facilitando búsquedas semánticas eficientes.

## Descripción General

- **Propósito:**  
  Conectar a una instancia de Redis y gestionar una base de datos vectorial (Vector DB) donde se almacenan documentos (por ejemplo, descripciones de tablas) convertidos en vectores. Permite cargar documentos, dividirlos en fragmentos, almacenarlos como vectores y realizar búsquedas semánticas sobre ellos.

- **Tecnologías utilizadas:**  
  - Redis (como base de datos vectorial)
  - LangChain (para embeddings y gestión de vectores)
  - Ollama (modelo de embeddings)
  - Python estándar (os, re, glob)

---

## Funciones Principales

### 1. `test_redis()`
**Descripción:**  
Verifica la conexión con la base de datos Redis.

**Inputs:**  
Ninguno.

**Output:**  
- `True` si la conexión es exitosa.
- `False` si ocurre un error.

---

### 2. `split_doc_content(doc_content, table_name=None)`
**Descripción:**  
Divide el contenido de un documento en secciones lógicas (tabla, descripción, columnas, llaves foráneas, índices) y fragmentos más pequeños para su vectorización.

**Inputs:**  
- `doc_content` (str): Contenido completo del documento.
- `table_name` (str, opcional): Nombre de la tabla. Si no se proporciona, se intenta extraer del contenido.

**Output:**  
- `chunks` (list[str]): Lista de fragmentos de texto.
- `table_name` (str): Nombre de la tabla extraído o proporcionado.

---

### 3. `create_vector_store()`
**Descripción:**  
Crea y configura una instancia de la base de datos vectorial en Redis, utilizando embeddings de Ollama.

**Inputs:**  
Ninguno.

**Output:**  
- Instancia de `RedisVectorStore`.

---

### 4. `load_docs()`
**Descripción:**  
Carga todos los documentos de la carpeta `Tables`, extrayendo su contenido y metadatos asociados.

**Inputs:**  
Ninguno.

**Output:**  
- `kbs` (dict): Diccionario con el nombre de la tabla como clave y el contenido del documento como valor.
- `metadata` (list[dict]): Lista de metadatos para cada documento.

---

### 5. `store_procedure()`
**Descripción:**  
Carga los documentos, los divide en fragmentos y los almacena como vectores en Redis junto con sus metadatos.

**Inputs:**  
Ninguno.

**Output:**  
Ninguno (efecto secundario: almacena los vectores en Redis).

---

### 6. `direct_query(text_input)`
**Descripción:**  
Ejecuta una consulta de ejemplo sobre la base de datos vectorial y muestra los resultados por consola.

**Inputs:**  
- `text_input` (str): Texto de consulta (aunque internamente usa una consulta fija de ejemplo).

**Output:**  
Ninguno (imprime resultados en consola).

---

### 7. `load_kb_to_redis()`
**Descripción:**  
Carga todos los documentos y los almacena en la base de datos vectorial de Redis.

**Inputs:**  
Ninguno.

**Output:**  
Ninguno.

---

### 8. `load_few_shots()`
**Descripción:**  
Carga ejemplos de prompts desde un archivo markdown.

**Inputs:**  
Ninguno.

**Output:**  
- Contenido del archivo `ReportsExample.md` (str).

---

### 9. `query_tables(input_text)`
**Descripción:**  
Realiza una búsqueda semántica en la base de datos vectorial y construye un contexto con los nombres de las tablas y el contenido relevante.

**Inputs:**  
- `input_text` (str): Texto de consulta.

**Output:**  
- `context` (str): Contexto generado a partir de los documentos relevantes.

---

### 10. `build_few_shot_prompt(text_input)`
**Descripción:**  
Construye un prompt de ejemplo para few-shot learning, incluyendo nombres de tablas y contexto relevante.

**Inputs:**  
- `text_input` (str): Texto de consulta.

**Output:**  
- `prompt` (str): Prompt generado.

---

### 11. `test_metadata()`
**Descripción:**  
Función de prueba que imprime un prompt generado para una consulta de ejemplo.

**Inputs:**  
Ninguno.

**Output:**  
Ninguno (imprime en consola).

---

## Notas Adicionales

- El módulo asume que los documentos a vectorizar están en la carpeta `Tables` y que el archivo de ejemplos está en `redis_db/ReportsExample.md`.
- La configuración de Redis y Ollama se realiza mediante variables de entorno (`REDIS_URL`, `OLLAMA_URL`).


Notas: redis_query_module esta no utilizado.