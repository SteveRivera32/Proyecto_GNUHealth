# Como montar la API


Para correr la apiu deberas bajar el repositiorio:
```bash 
git clone https://github.com/tu-usuario/Proyecto_GNUHealth.git
cd Proyecto_GNUHealth

```
# Opcion 1 instalacion con Anaconda

Si usas Anaconda crea un ambiente nuevo `venve` haciendo uso de 
tambien deberas activar elentorno con `conda activate` y usar `pip` para instalar las dependencias.
```bash
   conda create --name <nombre_del_entorno> python=3.11
   conda activate <nombre_del_entorno>
   pip install ollama
   pip install -U premsql
   pip install "fastapi[standard]"
   pip install "uvicorn[standard]"
   pip install tabulate
   pip install openai
   pip install pg8000
   pip install psycopg2-binary
   pip install redis
   pip install langchain_ollama
   pip install redisvl
   pip install langchain_redis

```
# Opcion 2 Instalacion via python venv
Si usas python venv deberas tener instalado python 3.11 y crear un python `venv`
usand:
```bash
# Crear un entorno virtual de Python (venv) llamado "venv" en el directorio padre de "API"
python3 -m venv ./venv

# Navegar al directorio "API"
cd API

# Activar el entorno virtual "venv"
# (El siguiente comando asume que estás en un sistema Unix/macOS.  Para Windows, usa "..\venv\Scripts\activate")
source ../venv/bin/activate

# Instalar las dependencias desde requirements.txt
pip install ollama
pip install -U premsql
pip install "fastapi[standard]"
pip install "uvicorn[standard]"
pip install tabulate
pip install openai
pip install pg8000
pip install psycopg2-binary

```


una vez las dependencias esten instaladas deberas correr en la carpeta de `API`
 ```bash
 cd API
fastapi dev main.py
```
Tambien puedes es correr este comando en lugar de fastapi para habilitar conexion de todos los puertos
```bash 
cd API
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
en open web ui deberas agregar la url de la API `https://localhost:8000`


# Configurando Variables de entorno:
ir al archivo `.venv` en la carpeta del proyecto.
```
OPENWEB_UI_URL=http://localhost:3000
MODEL_NAME=tinyllama
OLLAMA_URL=http://localhost:11434
OLLABA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=<API_KEY>


```
> Nota: Para  deberan hace que git omita los cambios del archivo .env
utlizando los comandos:

```
git rm .env --cached
git commit -m "Stopped tracking .env File"
```


# Configuracion de la base de datos:
Deberas descargar una de las copias de base de datso de gnu health
gnuhealth-44-demo.sql.gz

[Descargar Demos](https://www.gnuhealth.org/downloads/postgres_dumps/)

correr el siguiente comando:
```
docker build -t proyecto_gnuhealth-db .
```

luego para construir el container:

ATENCION: el siguiente comando deberas correrlo en caso de que no tengas 
los containers de OpenWeb UI y Ollama.

```
docker-compose up -d 
```








Pon el arhivo `gz` en el directorio del proyecto.
Abre docker:
```
docker cp gnuhealth-44-demo.sql.gz <container_id>:/tmp/
```
Ejecuta `docker ps` para ver los containers  y busca el id del proyecto gnu_health
```
docker exec -it <container_id> bash
```
Correr los siguientes dos comandos 
```
gunzip /tmp/gnuhealth-44-demo.sql.gz

# Import into the correct DB (e.g., ghdemo44)
psql -U admin -d ghdemo44 -f /tmp/gnuhealth-44-demo.sql

```
y por ultimo:
```
\dt 
```

listara las tablas de la base de datos.

> NOTA: Como recordatorio las credenciales de la base de datos son:

**Database:** ghdemo44

**Username:** admin

**Password:** gnusolidario

posgre corre en el puerto que 5432 
Adminer correra en el puerto 8080 y ahi podran visualizar la base de datos
En docker el  `Host` de los containers es el nombre, si usan adminer colocar 
la siguiente direccion en el campo server `nombre-container:5432`





