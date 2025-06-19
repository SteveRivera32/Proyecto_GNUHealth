# Asistente de GNUHealth

El Asistente de GNU Health es un proyecto en desarrollado y es impulsado por el uso de LLMs para la consulto de información a la base de datos de GNU Health. El proyecto hace uso de Open-WebUI como front end y una API de python creada con FastAPI.

![Static Badge](https://img.shields.io/badge/python-3.11%5E-green) ![Static Badge](https://img.shields.io/badge/Alfa-0.1-red) ![Static Badge](https://img.shields.io/badge/nuevas_dependencias-red)

# :brain: Asistente Virtual con Open WebUI + Ollama

Este proyecto usa [Open WebUI](https://github.com/open-webui/open-webui) como interfaz para interactuar con modelos LLM locales a través de [Ollama](https://ollama.com/), todo dentro de contenedores Docker para facilitar su instalación y uso en equipo.

---

## :rocket: Requisitos

Antes de comenzar, asegurarse de tener instalado:

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (incluye Docker y Docker Compose)
- WSL
- Ollama

> Docker Desktop debe estar corriendo, y habilitada la integración con WSL si usas Linux por medio de Windows.

---

## :tools: Instalación y Ejecución del Proyecto

1. **Variables de Entorno:**

   Debemos configuarar las variables de entorno de la siguiente forma:

   `OPENWEB_UI_URL`: host y puerto donde corre open web ui para la configuración del CORS.

   `REIS_URL`: host de la base de datos de redis con passwordless login.

   `OPENAI_API_KEY`: llave de openai o google cloud AI para conectarse a modelos mas grandes.(No implementado todavia)

```bash
   
OPENWEB_UI_URL=http://localhost:3000
OLLAMA_BASE_URL=http://localhost:11434
REDIS_URL=redis://:mypassword@localhost:6379
OPENAI_API_KEY=<OpenAIAPiKey>
```

1. **Clonar este repositorio:**

   Dentro de WSL ejecutar estos comandos:

   ```bash
   git clone https://github.com/SteveRivera32/Proyecto_GNUHealth.git
   cd Proyecto_GNUHealth
   ```

   Esto creará una carpeta con el nombre del proyecto.
2. **Configurar API**

   Primero instalar python venv y configurarlo:

   ```bash
   curl https://pyenv.run/ | bash
   export PYENV_ROOT="$HOME/.pyenv"
   command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
   eval "$(pyenv init -)"
   pyenv global 3.11
   ```

   Luego crear un venv:

   ```bash
   # Crear un entorno virtual de Python (venv) llamado "venv" en el directorio padre de "API"
   python3 -m venv ../venv
   ```

   Por último instalar las dependencias:

   ```bash
   # Navegar al directorio "API"
   cd API
   
   # Activar el entorno virtual "venv"
   source ../venv/bin/activate
   
   # Instalar las dependencias individualmente
   pip install ollama
   pip install premsql
   pip install fastapi[standard]
   pip install uvicorn[standard]
   pip install tabulate
   pip install openai
   pip install pg8000
   pip install psycopg2-binary
   pip install sqlalchemy
   pip install redis
   pip install langchain_ollama
   pip install redisvl
   pip install langchain_redis
   ```

   **NOTA:** Para desactivar el entorno venv:

   ```bash
   deactivate
   
   ```
3. **Levantar API**

   Para correrla se usa (dentro del entorno venv):

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   En el caso que el puerto 8000 ya esté siendo usado, se puede usar el 8001.

   **NOTA:** Para detenerla se usa "CTRL + C" en la terminal donde este corriendo.
4. **Configurar base de datos**

   En otra terminal, en el directorio del proyecto:

   ```bash
   docker build -t proyecto_gnuhealth-db .
   ```

   Levantar contenedor de OpenWebUI:

   ```bash
   docker-compose up -d 
   ```

   > Esto levantará OpenWebUI en el puerto 3000.

   Poner el arhivo gz en el directorio del proyecto:

   ```bash
   docker cp gnuhealth-44-demo.sql.gz <container_id>:/tmp/
   ```

   Ver los containers:

   ```bash
   docker ps
   ```

   Aquí buscar el ID de la imagen llamada "proyecto_gnuhealth-db". Copiarla y ejecutar los siguientes comandos:

   ```bash
   docker cp gnuhealth-44-demo.sql.gz <container_id>:/tmp/
   docker exec -it <container_id> bash
   gunzip /tmp/gnuhealth-44-demo.sql.gz
   psql -U admin -d ghdemo44 -f /tmp/gnuhealth-44-demo.sql
   ```

   **NOTA:** Para reiniciar o detener los contenedores (en el directorio del proyecto):

   ```bash
   docker-compose restart
   ```

   ```bash
   docker-compose down
   
   ```
5. **Correr Ollama localmente**

   En una nueva terminal, correr:

   ```bash
   ollama run <model_name>
   ```

   Recomendamos usar el modelo: **gemma3:4b**:

   ```bash
   ollama run gemma3:4b
   ```

   > Este modelo pesa aproximadamente 3gb
6. **Conectar API con OpenWebUI**

   Abrir OpenWebUI en el navegador: [http://localhost:3000](http://localhost:3000)

   Arriba a la derecha en su usuario, buscan la parte de "panel de administración", luego a configuración, luego conexiones y en la "API Ollama" deben quitar la URL que está y cambiarla por:

   ```bash
   http://host.docker.internal:8000
   ```

   > El puerto puede cambiar si levantaron la API en un puerto distinto a 8000.

   ![Image](https://github.com/user-attachments/assets/f5b8e614-362e-4a56-96ba-8b1778be4d44)

   Para saber si funciona la conexión con la API, revisar si ya aparecen modelos.
7. **Configuraciones necesarias en OpenWebUI**

   Arriba a la derecha en su usuario, van a ajustes y deben cambiar la sección de Interfaz (solo la parte de "chat"):

   ![Image](https://github.com/user-attachments/assets/6923922e-40a0-4836-8639-1cacd281472b)

   Luego en el "panel de administración", en configuración, también en Interfaz deben cambiar algunas cosas y dejarlo así:

   ![Image](https://github.com/user-attachments/assets/1bc64c63-54ff-4f39-be12-afd22d8aba4c)
8. **Agregar el prompt**

   Ahora deben crear un modelo en la sección de "espacio de trabajo" arriba a la izquierda. El modelo debe estar basado en un modelo disponible de Ollama. Agregan el siguiente prompt:

   ```bash
   You are an SQL expert specialized in the GNU Health database. You are part of an application system. Your job is to analyze natural language queries and return either an SQL query or a Markdown-formatted response, using strict JSON.
   
   You must always respond in one of the following three valid JSON formats:
   
   ---
   
   1. When the user query requires SQL execution:
   {"require": true, "sql": "SQL QUERY HERE"}
   
   - Only use this format when SQL is needed.
   - The query must be correct and based on the GNU Health schema.
   - Do not include explanations.
   - Do not wrap the output in code blocks or quotes.
   - Do NOT use Markdown outside.
   - Return only the JSON object.
   
   ---
   
   2. When the user query does not require SQL:
   {"content": "RESPONSE IN MARKDOWN"}
   
   - Use this format to explain, clarify, or answer general questions.
   - Respond using Markdown inside the "content" field.
   - Always respond in the same language the user used.
   - Do not include SQL unless the user asked for it.
   - Do not explain unless requested.
   
   ---
   
   3. When the SQL query you provided fails and the system returns an error:
   {"error": "ERROR MESSAGE HERE"}
   
   - This means your previous SQL query failed.
   - Analyze the error message and respond with either:
   a) A corrected SQL query using {"require": true, "sql": "..."}
   b) A Markdown explanation using {"content": "..."} if the error cannot be resolved in SQL.
   - Never return the error message directly to the user.
   - Always follow the same language used by the user.
   - Never break JSON formatting.
   
   ---
   
   Query execution:
   
   - The database engine is PostgreSQL.
   - You do not execute SQL.
   - When you return {"require": true, "sql": "..."}, the system will run the query and return the result to you.
   - The result will be in the following format:
   
       [
       {"Column1": "Value1", "Column2": "Value2"},
       {"Column1": "Value1", "Column2": "Value2"},
       ...
       ]
   
   - When you receive the result, respond using:
   {"content": "RESULT IN MARKDOWN"}
   
   - Format the result as a Markdown table if appropriate.
   - Do not generate a new SQL query.
   - Do not explain the data unless the user requested it.
   
   --
   
   Parsing issues:
   
   - If you receive a query result that is malformed or cannot be parsed, do not respond with a generic message.
   - Instead, return the following format to signal a data parsing issue:
   
   {"parse_error": "Could not parse the query result. Please check the format or structure."}
   
   - This helps the application detect and handle data parsing errors.
   - Do not use the {"content": "..."} format for this case.
   
   ---
   
   Multilingual behavior:
   
   - Match the language of the user in all responses.
   - If the user writes in Spanish, respond in Spanish.
   - If the user writes in English, respond in English.
   
   ---
   
   Strict rules:
   
   - Never include reasoning, or extra commentary.
   - Never return invalid JSON.
   - Never return multiple formats at once.
   - Never include code blocks or quotes around the JSON.
   
   ---
   synonims
   Condicion de salud = pathology
   Caso = patient
   ---
   
   Examples:
   User: Lista todas las enfermedades con su ID y nombre.
   Response:
   {"require": true, "sql": "SELECT id, name FROM gnuhealth_pathology;"}
   User question: Lista el número de casos por condicion de salud
   
   --
   ```

   Y en "parametros avanzados" deben desactivar la primera opción:

   ![Image](https://github.com/user-attachments/assets/d1239ea7-0bf3-4780-8993-19107cca9ae6)

   Recordar darle "guardar" abajo.
9. **Probar el proyecto**

   Para probar si funciona, deben seleccionar el modelo que acaban de crear y mandar un mensaje.
