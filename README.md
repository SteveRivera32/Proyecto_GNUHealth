# ⚠️ Advertencia
La branch "main" no está actualizada todavía, la funcional es "fixing_code_issues"

# 🧠 Asistente Virtual con Open WebUI + Ollama

Este proyecto usa [Open WebUI](https://github.com/open-webui/open-webui) como interfaz para interactuar con modelos LLM locales a través de [Ollama](https://ollama.com/), todo dentro de contenedores Docker para facilitar su instalación y uso en equipo.

---

## 🚀 Requisitos

Antes de comenzar, asegúrate de tener instalado en tu máquina:

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (incluye Docker y Docker Compose)
- (Opcional, pero recomendado) Git

> Docker Desktop debe estar corriendo, y habilitada la integración con WSL si usas Linux por medio de Windows.

---

## 🛠️ Instalación y Ejecución del Proyecto

1. **Clona este repositorio:**

   ```bash
   git clone https://github.com/tu-usuario/Proyecto_GNUHealth.git
   cd Proyecto_GNUHealth

2. **Los modelos se tienen que descargar localmente**

    En WSL:
    ```bash
    ollama run <nombre_del_modelo>

3. **Descargar imágenes y levantar contenedores**

   En el directorio del proyecto:
   ```bash
   docker-compose up -d

4. **Abrir OpenWebUI**

    En el navegador:
    http://localhost:3000

5. **Para reiniciar o detener los contenedores**
    
    En el directorio del proyecto:
    ```bash
    docker-compose restart
    ```
    
    ```bash
    docker-compose down


6. **Levantar Open AI endpoints**
 Para correr la apiu deberas bajar el repositiorio:
```bash 
git clone https://github.com/tu-usuario/Proyecto_GNUHealth.git
cd Proyecto_GNUHealth

```
Si usas conda crea un ambiente nuevo `venve` haciendo uso de 
tambien deberas activar elentorno con `conda activate` y usar `pip` para instalar las dependencias.
```bash
   conda create --name <nombre_del_entorno> python=3.11
   conda activate <nombre_del_entorno>
   pip install -r requirements.txt


```

Si usas python venv deberas tener instalado python 3.11 y crear un python `venv`
usand:
```bash
# Crear un entorno virtual de Python (venv) llamado "venv" en el directorio padre de "API"
python3 -m venv ../venv

# Navegar al directorio "API"
cd API

# Activar el entorno virtual "venv"
# (El siguiente comando asume que estás en un sistema Unix/macOS.  Para Windows, usa "..\venv\Scripts\activate")
source ../venv/bin/activate

# Instalar las dependencias desde requirements.txt
pip install -r requirements.txt

# Desactivar el entorno virtual (opcional)
deactivate

```


una vez las dependencias esten instaladas deberas correr en la carpeta de `API`
 ```bash
fastapi dev main.py
```
en open web ui deberas agregar la url de la API `https://localhost:8000`
![image](https://github.com/user-attachments/assets/73f3c7f6-aae3-433a-a827-c83d2aa14bdc)



