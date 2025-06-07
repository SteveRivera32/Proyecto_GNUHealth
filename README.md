
![Static Badge](https://img.shields.io/badge/python-3.11%5E-green)
![Static Badge](https://img.shields.io/badge/version-0.1-red)
![Static Badge](https://img.shields.io/badge/nuevas_dependencias-red)



# Atención
El proyecto esta configurado por defecto para conectarse a Ollama, recuerden editar .env file y asegurarse que ollama este corriendo y seleccionar
modelo que tengan instalados. En la API /`main.py` pueden modificar la lista actual de modelos.
Deberan revisar la nueva  ([Documentación](API/README.MD)) de la API para instalar la base de datos de GNU Health en docker.

# 🧠 Asistente Virtual con Open WebUI + Ollama

Este proyecto usa [Open WebUI](https://github.com/open-webui/open-webui) como interfaz para interactuar con modelos LLM locales a través de [Ollama](https://ollama.com/), todo dentro de contenedores Docker para facilitar su instalación y uso en equipo.

---

## 🚀 Requisitos

Antes de comenzar, asegurarse de tener instalado:

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (incluye Docker y Docker Compose)
- WSL
- Ollama

> Docker Desktop debe estar corriendo, y habilitada la integración con WSL si usas Linux por medio de Windows.

---

## 🛠️ Instalación y Ejecución del Proyecto

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
    >Esto levantará OpenWebUI en el puerto 3000.

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

5. **Configuraciones necesarias en OpenWebUI**
    
    Abrir OpenWebUI en el navegador:
    http://localhost:3000

    Arriba a la derecha en su usuario, van a ajustes y buscan la parte de "conexiones". Agregar una nueva y colocar la url:
    ```bash
    http://localhost:8000/api
    ```
    > El puerto puede cambiar si levantaron la API en uno distinto.

    También se recomienda agregar un prefijo para diferenciar los modelos de los locales de Ollama. El prefijo puede ser "prem".

    ![Image](https://github.com/user-attachments/assets/98c470ef-437d-4e62-b454-cbcd1d1eb5e6)

    Por último abajo a la izquierda en su usuario, ir a "administración", luego a ajustes, luego conexiones y en la "API Ollama" colocar el siguiente URL:
    ```bash
    http://host.docker.internal:11434
    ```

    ![Image](https://github.com/user-attachments/assets/8b940ad6-a2a1-4a76-b120-ab8835f551e2)

    Para saber si funciona la conexión con la API, revisar si ya aparecen modelos.

6. **Cambiar archivo .env**

    En el directorio del proyecto deberá aparecer un archivo .env (si no está crearlo). Aquí se debe colocar lo siguiente:
    ```bash
    OPENWEB_UI_URL=http://localhost:3000
    MODEL_NAME=<model_name>
    OLLAMA_URL=http://localhost:11434
    OPENAI_API_KEY=<key>
    ```

7. **Correr Ollama localmente**

    En una nueva terminal, correr:
    ```bash
    ollama run <model_name>
    ```

    Recomendamos usar el modelo: **anindya/prem1b-sql-ollama-fp116**:
    ```bash
    ollama run anindya/prem1b-sql-ollama-fp116
    ```

8. **Probar el proyecto**

    Para probar si funciona, deben primero apretar en "controles" (ícono al lado de las opciones de usuario) y desactivar "Transmisión Directa de la Respuesta del Chat".

    De esta manera ya debería funcionar mandarle un prompt. Importante recordar que el modelo no mantiene una conversación, solo responde a peticiones sobre la base de datos.
