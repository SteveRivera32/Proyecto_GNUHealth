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
