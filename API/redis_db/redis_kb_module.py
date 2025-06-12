from langchain_ollama import OllamaEmbeddings
import os
import redis
from langchain.text_splitter import RecursiveCharacterTextSplitter
from redis_db.redis_query_module import retriever
from langchain_redis import RedisConfig, RedisVectorStore
import re
from glob import glob
import re


REDIS_URL = os.getenv("REDIS_URL", "redis://:mypassword@localhost:6379")
# connection to host "redis" port 7379 with db 2 and password "secret" (old style authentication scheme without username / pre 6.x)
#redis://user:password@host:port/db 

def test_redis():
    print(f"Connecting to Redis at: {REDIS_URL}")
    #verify reddis connection:
    try:

        redis_client = redis.from_url(REDIS_URL)
        redis_client.ping()
        return True
    except Exception as e:
        print("Erro at URL:",e)
        return False



def split_doc_content(doc_content, table_name=None):
    # First extract table name from content if not provided
    if not table_name:
        match = re.search(r'^tabla:\s*(\w+)', doc_content, flags=re.MULTILINE)
        table_name = match.group(1) if match else "unknown"

    # Split by sections
    pattern = r'(?=^(tabla|descripción|columnas|llaves_foráneas|índices):)'
    raw_sections = re.split(pattern, doc_content, flags=re.MULTILINE)

    # Group headers with their contents
    sections = []
    i = 0
    while i < len(raw_sections):
        if raw_sections[i] in ["tabla", "descripción", "columnas", "llaves_foráneas", "índices"]:
            header = raw_sections[i]
            content = raw_sections[i + 1] if i + 1 < len(raw_sections) else ""
            full_section = f"{header}:{content}".strip()
            sections.append(full_section)
            i += 2
        else:
            i += 1

    # Split each section if too long
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = []
    for section in sections:
        section_chunks = splitter.split_text(section)
        chunks.extend(section_chunks)

    return chunks, table_name


def create_vector_store():


    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large",
        base_url=os.getenv("OLLAMA_URL", "http://localhost:11434")
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

def load_docs():
    folder_path = "Tables"
    pattern = os.path.join(folder_path, "*.txt")

    files = glob(pattern)
    kbs = {}
    metadata = []

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            file_name = os.path.basename(file_path)

            # Extraer nombre real de la tabla del contenido
            match = re.search(r'^tabla:\s*(\w+)', content, flags=re.MULTILINE)
            table_name = match.group(1) if match else file_name.replace(".txt", "")

            kbs[table_name] = content
            metadata.append({"category": table_name})

    return kbs, metadata



def store_procedure():
    if test_redis():
        vec_store = create_vector_store()

    kbs, metadata = load_docs()

    for i, (doc_name, content) in enumerate(kbs.items()):
        chunks, table_name = split_doc_content(content)
        # Create richer metadata for each chunk
        metas = [{
            "category": metadata[i]["category"],
            "table_name": table_name,
            "source": doc_name
        } for _ in chunks]
        vec_store.add_texts(chunks, metas)


def direct_query(text_input):
    query = "How to read the pregnancy table"
    vec=create_vector_store()
    results = vec.similarity_search(query, k=2)
    
    print("how to read pathology table")
    for doc in results:
        print(f"Content: {doc.page_content[:100]}...")
        print(f"Metadata: {doc.metadata}")
        print()
    
def load_kb_to_redis():
    store_procedure()

 

def load_few_shots():
    with open("redis_db/ReportsExample.md", "r", encoding="utf-8") as f:
        return f.read()
def query_tables(input_text):
    vector_store = create_vector_store()
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    
    # Retrieve relevant documents
    retrieved_docs = retriever.invoke(input_text)
    
    # Build context with table names and content
    context_parts = []
    for doc in retrieved_docs:
        table_name = doc.metadata.get("table_name", "unknown_table")
        context_parts.append(f"Table: {table_name}\n{doc.page_content}")
    
    context = "\n\n".join(context_parts)  # Double newline between entries
    return context

def build_few_shot_prompt(text_input):
    #few_shots = load_few_shots()
    context=query_tables(text_input)
    
    prompt = f"""
    table_names: 
    gnuhealth_patient_pregnancy,
    gnuhealth_patient_pathology,
    gnuhealth_patient_vaccination,
    gnuhealth_patient_disease,



    database context:
    {context}


    """
    return prompt



def test_metadata():
    #load_kb_to_redis()
    p=build_few_shot_prompt("How to read the pregnancy table")
    print(p)
