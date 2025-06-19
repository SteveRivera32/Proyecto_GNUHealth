
# Documentación de la clase `Agent`

## Descripción general

La clase `Agent` es un componente central que actúa como intermediario entre un modelo de lenguaje (LLM) y una base de datos SQL. Su objetivo es recibir preguntas en lenguaje natural, enriquecerlas con contexto relevante, enviar la consulta al modelo, interpretar la respuesta (que puede incluir instrucciones SQL), ejecutar dichas instrucciones en la base de datos y devolver los resultados de forma estructurada y amigable.

## Componentes principales

- **TextGenerator**: Módulo encargado de interactuar con el modelo de lenguaje (LLM). Recibe prompts y devuelve respuestas generadas.
- **Langchain SQLDatabase**: Permite la conexión y ejecución de consultas SQL sobre la base de datos relacional (en este caso, PostgreSQL).
- **redis_db.redis_kb_module**: Módulo que interactúa con una base de datos vectorial en Redis, utilizada para enriquecer el contexto que se le entrega al modelo de lenguaje.

---

## Flujo de funcionamiento

### 1. Enriquecimiento del contexto con datos vectoriales

Antes de enviar la pregunta al modelo, el agente utiliza el módulo `redis_db.redis_kb_module` para obtener contexto adicional relevante a la pregunta. Esto se realiza con la línea:

```python
extra_context = kb.build_few_shot_prompt(question) + "\n\n"
```

- **¿Qué hace?**  
  Llama a la función `build_few_shot_prompt` del módulo de Redis, que busca en la base de datos vectorial fragmentos de información relacionados con la pregunta. Este contexto se añade al prompt que se enviará al modelo, ayudando a que la respuesta sea más precisa y relevante.

---

### 2. Consulta al modelo de lenguaje

La función principal para interactuar con el modelo es `query_model`. El flujo es el siguiente:

- Se construye un historial de mensajes (chat history) que incluye la pregunta del usuario y el contexto enriquecido.
- Se envía este historial al modelo de lenguaje usando el método `generate` de `TextGenerator`.
- Se espera que el modelo devuelva una respuesta en formato JSON.
- Si la respuesta no es un JSON válido, se reintenta hasta 4 veces, indicando al modelo que corrija el formato.

---

### 3. Ejecución de consultas SQL

Si la respuesta del modelo incluye una instrucción SQL (campo `"sql"` en el JSON), el agente ejecuta la función:

```python
def execute_sql(self, sql: str):
```

- **¿Qué hace?**
  - Se conecta a la base de datos PostgreSQL usando `Langchain SQLDatabase`.
  - Ejecuta la consulta SQL recibida.
  - Convierte el resultado en un DataFrame de pandas.
  - Realiza conversiones necesarias para que los datos sean serializables (por ejemplo, fechas a string).
  - Devuelve los resultados como una lista de diccionarios (JSON).

- **Manejo de errores:**  
  Si ocurre un error al ejecutar la consulta, se informa al modelo para que intente corregir la instrucción SQL y se reintenta el proceso.

---

### 4. Formateo y respuesta

- Si el resultado es una lista de diccionarios, se convierte a una tabla Markdown para facilitar la visualización.
- Si es un diccionario simple, se muestra como un bloque de código JSON.
- El resultado final se añade al historial de la conversación y se devuelve al usuario.

---


## Ejemplo de uso

1. **Pregunta:** "¿Cuántos pacientes hay en la base de datos?"
2. **Contexto enriquecido:** Se añaden fragmentos relevantes desde Redis.
3. **Respuesta del modelo:**  
   ```json
   {
     "require": true,
     "sql": "SELECT COUNT(*) FROM patients"
   }
   ```
4. **Ejecución SQL:** El agente ejecuta la consulta y obtiene el resultado.
5. **Respuesta final:**  
   ```
   | count |
   |-------|
   |  123  |
   ```

---
