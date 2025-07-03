from langchain_ollama import OllamaEmbeddings
import os
import redis
from langchain.text_splitter import RecursiveCharacterTextSplitter
from redis_query_module import retriever
from langchain_redis import RedisConfig, RedisVectorStore
import re
from glob import glob

# URL de conexión a Redis. Por defecto se conecta a localhost:6379
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
def test_redis():
    """
    Verifica la conexión a Redis.
    
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    print(f"Connecting to Redis at: {REDIS_URL}")
    try:
        redis_client = redis.from_url(REDIS_URL)
        redis_client.ping()
        return True
    except Exception as e:
        print("Error at URL:", e)
        return False

def create_vector_store():
    """
    Crea y configura el almacén de vectores en Redis.
    
    Returns:
        RedisVectorStore: Instancia configurada del almacén de vectores
    """
    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large",
        base_url="http://localhost:11434"
    )
    config = RedisConfig(
        index_name="gnuhealth",
        redis_url=REDIS_URL,
        metadata_schema=[
            {"name": "category", "type": "tag"},
        ],
    )
    vector_store = RedisVectorStore(embeddings, config=config)
    return vector_store

def load_few_shots():
    """
    Carga ejemplos de reportes desde un archivo markdown.
    
    Returns:
        str: Contenido del archivo de ejemplos
    """
    with open("Reports-TableDocumentation/ReportsExample.md", "r", encoding="utf-8") as f:
        return f.read()

def query_tables(input_text):
    """
    Realiza una búsqueda por similitud en las tablas usando el texto de entrada.
    
    Args:
        input_text (str): Texto de consulta
        
    Returns:
        str: Contexto construido con la información relevante de las tablas
    """
    vector_store = create_vector_store()
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    
    # Recuperar documentos relevantes
    retrieved_docs = retriever.invoke(input_text)
    
    # Construir contexto con nombres de tablas y contenido
    context_parts = []
    for doc in retrieved_docs:
        table_name = doc.metadata.get("category", "unknown_table")
        context_parts.append(f" Table: {table_name}\n{doc.page_content}")
    
    context = "\n\n".join(context_parts)
    return context


def load_docs():
    folder_path = "./Tables"
    pattern = os.path.join(folder_path, "*.txt")

    files = glob(pattern)
    kbs = {}
    metadata = []

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            file_name = os.path.basename(file_path)
            kbs[file_name] = content
            
            # Derivar categoría desde nombre de archivo sin extensión
            category_name = file_name.replace("_table_gpt.txt", "").replace(".txt", "").strip()
            metadata.append({"category": category_name})

    

    return kbs, metadata


def store_procedure():
    if test_redis():
        vec_store = create_vector_store()

    kbs, metadata = load_docs()
    print(kbs)
    vec_store.add_texts(kbs.values(),metadata)




def build_few_shot_prompt(text_input):
    """
    Construye un prompt utilizando ejemplos y el contexto de las tablas.
    
    Args:
        text_input (str): Texto de entrada para la consulta
        
    Returns:
        str: Prompt construido con el contexto y ejemplos
    """
    #few_shots = load_few_shots()
    context = query_tables(text_input)
    
    prompt = f"""
    database context:
    {context}
    """
    return prompt

def test_metadata():
    """
    Función de prueba que construye un prompt para listar enfermedades
    """
    p = build_few_shot_prompt("Lista un reporte de las enfermedades")
    print(p)

if __name__ == "__main__":
    store_procedure()