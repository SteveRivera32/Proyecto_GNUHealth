
![Static Badge](https://img.shields.io/badge/python-3.11%5E-green)
![Static Badge](https://img.shields.io/badge/version-0.1-red)
![Static Badge](https://img.shields.io/badge/nuevas_dependencias-red)

# 🧠 Asistente Virtual con Open WebUI + Ollama

Este proyecto usa [Open WebUI](https://github.com/open-webui/open-webui) como interfaz para interactuar con modelos LLM locales a través de [Ollama](https://ollama.com/), todo dentro de contenedores Docker para facilitar su instalación y uso en equipo.

---

## 🚀 Requisitos

Antes de comenzar, asegurarse de tener instalado:

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (incluye Docker y Docker Compose)
- WSL


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
    ```

    Para desactivar el entorno venv:
    ```bash
    deactivate

    ```

3. **Levantar API**

    Para correrla se usa (dentro del entorno venv):
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    
    En el caso que el puerto 8000 ya esté siendo usado, se puede usar el 8001.

    Para detenerla se usa "CTRL + C" en la terminal donde este corriendo.

4. **Descargar imágenes y levantar contenedores**

   En otra terminal, en el directorio del proyecto:
   ```bash
   docker-compose up -d
   ```
    Esto levantará OpenWebUI en el puerto 3000.

    Para reiniciar o detener los contenedores (en el directorio del proyecto):
    ```bash
    docker-compose restart
    ```
    
    ```bash
    docker-compose down

5. **Configuraciones necesarias en OpenWebUI**
    
    Abrir OpenWebUI en el navegador:
    http://localhost:3000

    Arriba a la derecha en su usuario, van a ajustes y buscan la parte de "conexiones". Agregar una nueva y colocar la url: http://localhost:8000/api
    > El puerto puede cambiar si levantaron la API en uno distinto.

    ![image](https://github.com/user-attachments/assets/73f3c7f6-aae3-433a-a827-c83d2aa14bdc)

    Por último deben apretar en "controles" (ícono al lado de las opciones de usuario) y desactivar "Transmisión Directa de la Respuesta del Chat".

    Para saber si funciona la conexión con la API, revisar si ya aparecen modelos.



