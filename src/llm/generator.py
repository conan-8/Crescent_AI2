# src/llm/generator.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from typing import List
from src import config


def generate_answer(query: str, context: List[str]):
    """
    Generates an answer using Gemini based on the query and context.
    """
    
    prompt_template = """
    You are a helpful AI assistant for Crescent School. Use the following pieces of context to answer the user's question. If you don't know the answer from the context provided, just say that you don't know, don't try to make up an answer.

    Context:
    ---
    {context}
    ---

    Question: {question}

    Answer:
    """
    
    prompt = PromptTemplate.from_template(prompt_template)
    
    llm = ChatGoogleGenerativeAI(
        model=config.GENERATION_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=0.3  # Controls creativity, lower is more factual
    )

    # This is a simple LangChain "chain" to structure the process
    rag_chain = (
        {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Format the context from a list of strings into a single string
    formatted_context = "\n\n".join(context)

    # Invoke the chain with the required inputs
    answer = rag_chain.invoke({"context": formatted_context, "question": query})
    
    return answer