from redisvl.query.filter import Tag
def similarity_search(text_input,category,vector_store):
    query = text_input
    
    # Create a RedisVL filter expression
    filter_condition = Tag("category") == category
    
    filtered_results = vector_store.similarity_search(query, k=2, filter=filter_condition)
    
    print("Filtered Similarity Search Results:")
    for doc in filtered_results:
        print(f"Content: {doc.page_content[:100]}...")
        print(f"Metadata: {doc.metadata}")
        print()



def retriever(input_text,vector_store):
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    return retriever.invoke(input_text)
