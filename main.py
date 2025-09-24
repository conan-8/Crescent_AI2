from src.vector_store.database_manager import ChromaManager
from src.llm.generator import generate_answer
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src import config

def main():
    """
    The main application loop for the AI search tool.
    """
    # Initialize the components
    db_manager = ChromaManager()
    
    # We only need the embedding function for the user's query
    embedding_function = GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        google_api_key=config.GOOGLE_API_KEY
    )

    print("--- Crescent AI Search Tool ---")
    print("Ask a question, or type 'exit' to quit.")

    while True:
        query = input("\nYour question: ")
        if query.lower() == 'exit':
            break

        # 1. Create an embedding for the user's query
        query_embedding = embedding_function.embed_query(query)

        # 2. Retrieve relevant context from the database
        context = db_manager.query(query_embedding, n_results=3)

        # 3. Generate an answer using the LLM
        answer = generate_answer(query, context)

        print("\nAnswer:")
        print(answer)

if __name__ == "__main__":
    main()
