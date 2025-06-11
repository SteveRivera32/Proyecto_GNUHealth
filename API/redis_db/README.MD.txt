# Como usar este modulo de forma aislada?

debes create un container de Redis-Stack  acorde a https://hub.docker.com/r/redis/redis-stack


```python
load_kb_to_redis()
```

Corre esta funcion para cargar a la base de datos de redis.

Tambien tendras que hacer uso de ``build_few_shot_protmpo(text_input) para realizar una busqueda semantica y retornar l
un prompt para el llm

```python
def build_few_shot_prompt(text_input):
    few_shots = load_few_shots()
    context=query_tables("text_input")
    
    prompt = f"""
    database context:
    {context}
    


    You are a helpful assistant that provides information about GNU Health tables.
    Use the following examples to understand how to answer questions about the tables:

    {few_shots}

    Now, answer the user's question based on the provided examples.
    """
    return prompt





```